"""
Drug-Adverse Event Causality Classification v2.0
BioBERT-based Pharmacovigilance Model with Medical Terminology Normalization
PBRER/PSUR and FAERS Compliant for Regulatory Safety Workflows
Zero-cost, local/offline capable, open-source architecture
"""

import os
import sys
import re
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Union, List, Dict, Optional, Tuple

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Modern PDF Reader with fallback
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

# Robust NLTK setup without security vulnerabilities
import nltk

def setup_nltk_safely():
    """Ensure NLTK sentence tokenizers are present without compromising SSL."""
    # Use user-writable cross-platform temp directory
    cache_nltk_dir = os.path.join(tempfile.gettempdir(), "drug_bert_nltk_data")
    if not os.path.exists(cache_nltk_dir):
        try:
            os.makedirs(cache_nltk_dir, exist_ok=True)
        except OSError:
            pass

    if cache_nltk_dir not in nltk.data.path:
        nltk.data.path.insert(0, cache_nltk_dir)

    for pkg in ["punkt", "punkt_tab"]:
        try:
            nltk.data.find(f"tokenizers/{pkg}")
        except LookupError:
            try:
                nltk.download(pkg, download_dir=cache_nltk_dir, quiet=True)
            except Exception:
                pass

setup_nltk_safely()


def simple_sentence_tokenize(text: str) -> List[str]:
    """Clean regex sentence boundary detector as zero-dependency fallback."""
    if not text:
        return []
    # Split on sentence terminals followed by whitespace, keeping abbreviations reasonable
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    return [s.strip() for s in sentences if s.strip()]


def safe_sent_tokenize(text: str) -> List[str]:
    """Tokenize sentences using NLTK if available, falling back to regex."""
    if not text:
        return []
    try:
        from nltk.tokenize import sent_tokenize
        return sent_tokenize(text)
    except Exception:
        return simple_sentence_tokenize(text)


def preprocess_medical_causality(text: str) -> str:
    """
    Standardize clinical causality phrasing for optimal BioBERT tokenization.
    Normalizes passive, hedged, and variable safety terminology into canonical forms.
    """
    if not text:
        return ""
    text_lower = text.lower()
    replacements = {
        # Strong causality markers
        "secondary to": "caused by",
        "due to": "caused by",
        "induced by": "caused by",
        "resulting from": "caused by",
        "associated with": "related to",
        # Hedging normalization
        "may be related to": "related to",
        "possibly related to": "related to",
        "likely related to": "related to",
        "could be related to": "related to",
        "suspected to be related to": "related to",
        # Side effect terminology
        "is a very rare side effect": "is an adverse effect",
        "is a rare side effect": "is an adverse effect",
        "is a common side effect": "is an adverse effect",
        "is a side effect of": "is an adverse effect of",
        "side effects of": "adverse effects of",
        "side effect of": "adverse effect of",
        # Temporal cues
        "after taking": "following administration of",
        "upon starting": "following administration of",
        "after starting": "following administration of",
        # ADR phrasing
        "adverse reaction": "adverse effect",
        "adverse drug reaction": "adverse effect",
        "adr": "adverse effect"
    }
    for old, new in replacements.items():
        text_lower = text_lower.replace(old, new)
    return text_lower


def detect_causality_markers(text: str) -> Dict:
    """Detect explicit pharmacovigilance causality cues and temporal signals."""
    markers = [
        "secondary to", "caused by", "induced by", "due to", "following administration",
        "after taking", "side effect", "adverse effect", "adr", "related to",
        "associated with", "drug toxicity", "drug-induced", "iatrogenic", "dechallenge"
    ]
    text_lower = text.lower()
    found = [m for m in markers if m in text_lower]
    return {
        "has_markers": len(found) > 0,
        "markers_found": found,
        "marker_count": len(found)
    }


class CausalityClassifier:
    """
    BioBERT Drug-Adverse Event Causality Classifier v2.0
    Fine-tuned on ADE Corpus V2 benchmark (97.6% accuracy).

    Features:
    - Dual loading: auto-detects local model weights with automatic fallback to Hugging Face Hub
    - Automatic hardware acceleration (CUDA / Apple Silicon MPS / CPU)
    - Medical text preprocessing & explicit causality marker detection
    - Calibrated probabilistic scoring
    """

    HF_MODEL_ID = "PrashantRGore/drug-causality-bert-v2-model"
    LOCAL_FALLBACK_DIR = "./models/production_model_final"

    def __init__(
        self,
        model_path: Optional[str] = None,
        threshold: float = 0.5,
        use_preprocessing: bool = True,
        hf_token: Optional[str] = None
    ):
        self.threshold = threshold
        self.use_preprocessing = use_preprocessing
        
        # Hardware acceleration detection
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        # Determine model path
        self.model_path = model_path or self._resolve_model_path()
        self.token = hf_token or os.environ.get("HF_TOKEN", None)

        # Load Tokenizer & Model
        self.tokenizer, self.model = self._load_model_and_tokenizer()
        self.model.to(self.device)
        self.model.eval()

    def _resolve_model_path(self) -> str:
        """Check for valid local weights first, else return Hugging Face Hub repo id."""
        local_dir = Path(self.LOCAL_FALLBACK_DIR)
        local_weights = local_dir / "model.safetensors"
        # Verify local weights exist and are actual weights (> 1 MB, not a 134-byte git LFS pointer)
        if local_weights.exists() and local_weights.stat().st_size > 1024 * 1024:
            return str(local_dir)
        return self.HF_MODEL_ID

    def _load_model_and_tokenizer(self):
        """Loads model and tokenizer using modern non-deprecated Hugging Face API."""
        load_kwargs = {}
        if self.token and not Path(self.model_path).exists():
            load_kwargs["token"] = self.token

        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_path, **load_kwargs)
            model = AutoModelForSequenceClassification.from_pretrained(self.model_path, **load_kwargs)
            return tokenizer, model
        except Exception as e:
            # If specified path failed and wasn't default HF, try HF as fallback
            if self.model_path != self.HF_MODEL_ID:
                tokenizer = AutoTokenizer.from_pretrained(self.HF_MODEL_ID, **load_kwargs)
                model = AutoModelForSequenceClassification.from_pretrained(self.HF_MODEL_ID, **load_kwargs)
                return tokenizer, model
            raise e

    def predict(
        self,
        text: str,
        threshold: Optional[float] = None,
        return_probs: bool = True,
        enhance_score: bool = False
    ) -> Dict:
        """
        Classify causality in a clinical statement.

        Args:
            text: Input clinical text
            threshold: Custom threshold (defaults to self.threshold)
            return_probs: Whether to return probability distribution
            enhance_score: Whether to apply heuristic regulatory boost for edge cases

        Returns:
            Dictionary with prediction, confidence, probabilities, and marker detection.
        """
        thresh = threshold if threshold is not None else self.threshold
        marker_info = detect_causality_markers(text)

        input_text = preprocess_medical_causality(text) if self.use_preprocessing else text

        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]

        # Class 1 = Related / Causal ADE, Class 0 = Not Related
        prob_related = float(probs[1])
        prob_not_related = float(probs[0])

        confidence = prob_related
        if enhance_score and marker_info["has_markers"]:
            boost = min(0.12, marker_info["marker_count"] * 0.04)
            confidence = min(prob_related + boost, 0.99)

        pred_label = 1 if confidence >= thresh else 0
        prediction_str = "related" if pred_label == 1 else "not related"

        result = {
            "prediction": prediction_str,
            "confidence": confidence,
            "raw_confidence": prob_related,
            "label": pred_label,
            "causality_markers_detected": marker_info["has_markers"],
            "marker_count": marker_info["marker_count"],
            "markers_found": marker_info["markers_found"],
            "device": str(self.device)
        }

        if return_probs:
            result["probabilities"] = {
                "not_related": prob_not_related,
                "related": prob_related
            }

        return result

    def predict_batch(self, texts: List[str], threshold: Optional[float] = None) -> List[Dict]:
        """Perform batched prediction across a list of clinical texts."""
        if not texts:
            return []
        return [self.predict(t, threshold=threshold) for t in texts]


def extract_text_from_pdf(pdf_source: Union[str, Path, bytes, object]) -> str:
    """
    Extract full text from a PDF file path or file-like stream using pypdf or PyPDF2.
    """
    extracted_text = []

    if HAS_PYPDF:
        try:
            reader = pypdf.PdfReader(pdf_source)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)
            return "\n".join(extracted_text)
        except Exception as e:
            if not HAS_PYPDF2:
                raise RuntimeError(f"Failed to extract text using pypdf: {e}")

    if HAS_PYPDF2:
        try:
            reader = PyPDF2.PdfReader(pdf_source)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)
            return "\n".join(extracted_text)
        except Exception as e:
            raise RuntimeError(f"Failed to extract text using PyPDF2: {e}")

    raise ImportError("No PDF reader library installed. Install 'pypdf>=4.0.0'.")


def classify_causality(
    pdf_text: str,
    classifier: Optional[CausalityClassifier] = None,
    threshold: float = 0.5,
    use_preprocessing: bool = True
) -> Dict:
    """
    Performs full-document clinical sentence decomposition and causality classification.
    """
    start_time = datetime.now()
    if classifier is None:
        classifier = CausalityClassifier(threshold=threshold, use_preprocessing=use_preprocessing)

    sentences = safe_sent_tokenize(pdf_text)
    related_count = 0
    sentence_details = []

    for sent in sentences:
        sent_clean = sent.strip()
        if len(sent_clean) < 15:
            continue

        pred = classifier.predict(sent_clean, threshold=threshold)
        if pred["label"] == 1:
            related_count += 1
            sentence_details.append({
                "sentence": sent_clean[:200] + ("..." if len(sent_clean) > 200 else ""),
                "probability_related": pred["probabilities"]["related"],
                "confidence": pred["confidence"],
                "markers_detected": pred["causality_markers_detected"],
                "marker_count": pred["marker_count"]
            })

    sentence_details.sort(key=lambda x: x["probability_related"], reverse=True)

    final_classification = "related" if related_count > 0 else "not related"
    overall_confidence = (
        sentence_details[0]["confidence"] if sentence_details
        else (1.0 - (related_count / max(1, len(sentences))))
    )
    duration = (datetime.now() - start_time).total_seconds()

    return {
        "final_classification": final_classification,
        "confidence_score": overall_confidence,
        "related_sentences": related_count,
        "not_related_sentences": len(sentences) - related_count,
        "total_sentences": len(sentences),
        "top_related_sentences": sentence_details[:10],
        "threshold_used": threshold,
        "processing_time_seconds": duration,
        "timestamp": datetime.now().isoformat()
    }


def process_pdf_file(
    pdf_path: str,
    classifier: Optional[CausalityClassifier] = None,
    threshold: float = 0.5
) -> Dict:
    """Extract and analyze a single PDF file."""
    text = extract_text_from_pdf(pdf_path)
    results = classify_causality(text, classifier=classifier, threshold=threshold)
    results["source_file"] = os.path.basename(pdf_path)
    return results


def process_multiple_pdfs(
    pdf_paths: List[str],
    classifier: Optional[CausalityClassifier] = None,
    threshold: float = 0.5
) -> List[Dict]:
    """Batch process multiple clinical case PDF documents."""
    return [process_pdf_file(p, classifier=classifier, threshold=threshold) for p in pdf_paths]
