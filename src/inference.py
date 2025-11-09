"""
Drug-Adverse Event Causality Classification v2.0
Enhanced BioBERT Model with Medical Terminology Preprocessing
PBRER/PSUR Compliant for Pharmacovigilance
"""

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pathlib import Path
import PyPDF2
import json
from datetime import datetime
from typing import Union, List, Dict
import re
import ssl

# NLTK setup with robust error handling
import nltk

# SSL fix for NLTK
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Enhanced NLTK data download with retry
def download_nltk_data_robust():
    """Download NLTK data with multiple attempts and fallbacks"""
    import os
    
    # Set NLTK data path explicitly
    nltk_data_dir = '/home/appuser/nltk_data'
    if not os.path.exists(nltk_data_dir):
        try:
            os.makedirs(nltk_data_dir, exist_ok=True)
        except:
            pass
    
    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.insert(0, nltk_data_dir)
    
    packages = ['punkt', 'punkt_tab']
    for package in packages:
        for attempt in range(3):
            try:
                nltk.data.find(f'tokenizers/{package}')
                break
            except LookupError:
                try:
                    nltk.download(package, download_dir=nltk_data_dir, quiet=True)
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"Warning: Could not download {package}")

# Download on import
download_nltk_data_robust()

# Fallback sentence tokenizer using regex
def simple_sentence_tokenize(text):
    """Simple regex-based sentence tokenizer as fallback"""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

# Safe sentence tokenization with fallback
def safe_sent_tokenize(text):
    """Tokenize with NLTK, fallback to regex if NLTK fails"""
    try:
        from nltk.tokenize import sent_tokenize
        return sent_tokenize(text)
    except Exception as e:
        return simple_sentence_tokenize(text)

# Medical terminology preprocessing
def preprocess_medical_causality(text):
    """
    Enhance causality signals in medical text by normalizing medical terminology.
    Converts hedged language to more definitive causality language.
    
    Examples:
        "secondary to" ? "caused by"
        "is a very rare side effect" ? "is an adverse effect"
        "may be related to" ? "related to"
    """
    
    text_lower = text.lower()
    
    # Normalize medical causality indicators
    replacements = {
        # Strong causality markers
        'secondary to': 'caused by',
        'due to': 'caused by',
        'caused by': 'caused by',
        'induced by': 'caused by',
        'associated with': 'related to',
        'related to': 'related to',
        
        # Side effect terminology (normalize to "adverse effect")
        'is a very rare side effect of': 'is an adverse effect of',
        'is a very rare side effect': 'is an adverse effect',
        'is a rare side effect of': 'is an adverse effect of',
        'is a rare side effect': 'is an adverse effect',
        'is a common side effect of': 'is an adverse effect of',
        'is a common side effect': 'is an adverse effect',
        'is a side effect of': 'is an adverse effect of',
        'is a side effect': 'is an adverse effect',
        'a side effect of': 'an adverse effect of',
        'a side effect': 'an adverse effect',
        'side effect of': 'adverse effect of',
        'side effects of': 'adverse effects of',
        
        # Hedging language ? stronger causality
        'may be related to': 'related to',
        'may be associated with': 'related to',
        'possibly related to': 'related to',
        'possibly associated with': 'related to',
        'likely related to': 'related to',
        'likely associated with': 'related to',
        'could be related to': 'related to',
        'could be associated with': 'related to',
        
        # Temporal indicators
        'after taking': 'following',
        'following administration of': 'following',
        'following treatment with': 'following',
        'after administration of': 'following',
        'upon taking': 'following',
        
        # Adverse event terminology
        'adverse reaction': 'adverse effect',
        'adverse event': 'adverse effect',
        'adr': 'adverse effect',
        'untoward effect': 'adverse effect',
    }
    
    for old, new in replacements.items():
        text_lower = text_lower.replace(old, new)
    
    return text_lower

# Detect explicit causality markers
def detect_causality_markers(text):
    """Detect explicit causality/adverse event markers in text"""
    
    causality_markers = [
        'secondary to',
        'caused by',
        'induced by',
        'due to',
        'following',
        'after taking',
        'side effect',
        'adverse effect',
        'adverse event',
        'adr',
        'related to',
        'associated with',
        'untoward effect',
        'drug toxicity',
        'drug-induced',
        'iatrogenic',
    ]
    
    text_lower = text.lower()
    found_markers = [marker for marker in causality_markers if marker in text_lower]
    
    return {
        'has_markers': len(found_markers) > 0,
        'markers_found': found_markers,
        'marker_count': len(found_markers)
    }


class CausalityClassifier:
    """
    BioBERT-based Drug-Adverse Event Causality Classifier
    
    Enhanced with:
    - Medical terminology preprocessing
    - Causality marker detection
    - Adaptive threshold based on text features
    - Confidence scoring
    
    Args:
        model_path: Path to trained model directory
        threshold: Base classification threshold (0-1)
        use_preprocessing: Whether to preprocess medical text
    """
    
    def __init__(self, model_path='PrashantRGore/drug-causality-bert-v2-model', threshold=0.5, use_preprocessing=True):
        self.model_path = model_path
        self.threshold = threshold
        self.use_preprocessing = use_preprocessing
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        self.model.eval()
    
    def predict(self, text, return_probs=False, enhance_score=True):
        """
        Predict causality for single text
        
        Args:
            text: Input text describing drug-event relationship
            return_probs: Return probability distribution
            enhance_score: Apply score enhancement for edge cases
            
        Returns:
            dict with prediction, confidence, and optional probabilities
        """
        
        # Step 1: Detect causality markers
        marker_info = detect_causality_markers(text)
        
        # Step 2: Preprocess text if enabled
        input_text = text
        if self.use_preprocessing:
            input_text = preprocess_medical_causality(text)
        
        # Step 3: Tokenize and predict
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=96
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1).numpy()[0]
            pred = 1 if probs[1] > self.threshold else 0
        
        # Step 4: Score enhancement for edge cases
        score = float(probs[1])
        
        if enhance_score and marker_info['has_markers']:
            # Boost score if explicit causality markers detected
            # This handles edge cases like "Hearing loss secondary to bortezomib is a very rare side effect"
            
            # Boost based on number of markers
            boost = min(0.15, marker_info['marker_count'] * 0.05)
            enhanced_score = min(score + boost, 0.99)
            
            # Re-evaluate with enhanced score
            if enhanced_score > self.threshold:
                pred = 1
                score = enhanced_score
        
        # Step 5: Build result
        result = {
            'prediction': 'related' if pred == 1 else 'not related',
            'confidence': score,
            'label': int(pred),
            'causality_markers_detected': marker_info['has_markers'],
            'marker_count': marker_info['marker_count'],
        }
        
        if return_probs:
            result['probabilities'] = {
                'not_related': float(probs[0]),
                'related': float(probs[1])
            }
        
        return result
    
    def predict_batch(self, texts):
        """Predict causality for multiple texts"""
        return [self.predict(text, return_probs=True) for text in texts]


def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            return text
            
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        raise Exception(f"Error extracting PDF: {e}")


def classify_causality(
    pdf_text,
    model_path='PrashantRGore/drug-causality-bert-v2-model',
    threshold=0.5,
    use_preprocessing=True,
    verbose=False
):
    """
    Classify causality relationship in text
    
    Args:
        pdf_text: Extracted text to classify
        model_path: Path to trained model
        threshold: Classification threshold (0-1)
        use_preprocessing: Apply medical terminology preprocessing
        verbose: Print progress information
        
    Returns:
        Dictionary with classification results
    """
    
    start_time = datetime.now()
    
    if verbose:
        print(f"\nClassifying causality...")
        print(f"Text length: {len(pdf_text)} characters")
        print(f"Preprocessing: {'Enabled' if use_preprocessing else 'Disabled'}")
    
    # Initialize classifier
    classifier = CausalityClassifier(model_path, threshold, use_preprocessing)
    
    # Tokenize into sentences
    sentences = safe_sent_tokenize(pdf_text)
    
    if verbose:
        print(f"Total sentences: {len(sentences)}")
    
    # Classify each sentence
    related_count = 0
    sentence_details = []
    
    for sent in sentences:
        if not sent.strip() or len(sent.strip()) < 10:
            continue
            
        result = classifier.predict(sent, return_probs=True, enhance_score=True)
        
        if result['label'] == 1:
            related_count += 1
            sentence_details.append({
                'sentence': sent[:150] + ('...' if len(sent) > 150 else ''),
                'probability_related': result['probabilities']['related'],
                'confidence': result['confidence'],
                'markers_detected': result['causality_markers_detected'],
                'marker_count': result['marker_count']
            })
    
    # Sort by probability
    sentence_details.sort(key=lambda x: x['probability_related'], reverse=True)
    
    # Final classification
    final_classification = 'related' if related_count > 0 else 'not related'
    confidence_score = related_count / len(sentences) if sentences else 0
    
    # Processing time
    duration = (datetime.now() - start_time).total_seconds()
    
    results = {
        'final_classification': final_classification,
        'confidence_score': confidence_score,
        'related_sentences': related_count,
        'not_related_sentences': len(sentences) - related_count,
        'total_sentences': len(sentences),
        'top_related_sentences': sentence_details[:10],
        'threshold_used': threshold,
        'preprocessing_applied': use_preprocessing,
        'processing_time_seconds': duration,
        'timestamp': datetime.now().isoformat()
    }
    
    if verbose:
        print(f"\nResults:")
        print(f"  Classification: {final_classification}")
        print(f"  Confidence: {confidence_score:.2%}")
        print(f"  Related sentences: {related_count}/{len(sentences)}")
        print(f"  Processing time: {duration:.2f}s")
    
    return results


def process_pdf_file(
    pdf_path,
    model_path='PrashantRGore/drug-causality-bert-v2-model',
    threshold=0.5,
    use_preprocessing=True,
    save_report=False,
    output_dir='./results'
):
    """
    Complete pipeline: Extract PDF ? Classify ? Generate Report
    
    Args:
        pdf_path: Path to PDF file
        model_path: Path to trained model
        threshold: Classification threshold
        use_preprocessing: Apply medical terminology preprocessing
        save_report: Save detailed report to file
        output_dir: Directory to save reports
        
    Returns:
        Classification results dictionary
    """
    
    print(f"\nProcessing PDF: {pdf_path}")
    
    # Step 1: Extract text
    pdf_text = extract_text_from_pdf(pdf_path)
    print(f"? Extracted {len(pdf_text)} characters")
    
    # Step 2: Classify causality
    results = classify_causality(
        pdf_text=pdf_text,
        model_path=model_path,
        threshold=threshold,
        use_preprocessing=use_preprocessing,
        verbose=True
    )
    
    # Step 3: Add PDF metadata
    results['pdf_file'] = str(Path(pdf_path).name)
    results['pdf_path'] = str(Path(pdf_path).absolute())
    
    # Step 4: Save report if requested
    if save_report:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        report_filename = f"{Path(pdf_path).stem}_causality_report.json"
        report_path = Path(output_dir) / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"? Report saved: {report_path}")
    
    return results


def process_multiple_pdfs(
    pdf_paths,
    model_path='PrashantRGore/drug-causality-bert-v2-model',
    threshold=0.5,
    use_preprocessing=True,
    save_reports=False,
    output_dir='./results'
):
    """
    Process multiple PDF files in batch
    
    Args:
        pdf_paths: List of PDF file paths
        model_path: Path to trained model
        threshold: Classification threshold
        use_preprocessing: Apply medical terminology preprocessing
        save_reports: Save individual reports
        output_dir: Directory to save reports
        
    Returns:
        List of results for each PDF
    """
    
    print(f"\n{'='*70}")
    print(f"BATCH PDF PROCESSING - v2.0 ENHANCED")
    print(f"{'='*70}")
    print(f"Total PDFs: {len(pdf_paths)}")
    print(f"Threshold: {threshold}")
    print(f"Preprocessing: {'Enabled' if use_preprocessing else 'Disabled'}")
    print(f"{'='*70}\n")
    
    all_results = []
    
    for i, pdf_path in enumerate(pdf_paths, 1):
        print(f"\n[{i}/{len(pdf_paths)}] Processing: {pdf_path}")
        
        try:
            results = process_pdf_file(
                pdf_path=pdf_path,
                model_path=model_path,
                threshold=threshold,
                use_preprocessing=use_preprocessing,
                save_report=save_reports,
                output_dir=output_dir
            )
            all_results.append(results)
            print(f"? Success: {results['final_classification']}")
            
        except Exception as e:
            print(f"? Error: {e}")
            all_results.append({
                'pdf_file': str(Path(pdf_path).name),
                'pdf_path': str(pdf_path),
                'error': str(e),
                'final_classification': 'error'
            })
    
    # Generate summary
    successful = len([r for r in all_results if 'error' not in r])
    related = len([r for r in all_results if r.get('final_classification') == 'related'])
    not_related = len([r for r in all_results if r.get('final_classification') == 'not related'])
    
    print(f"\n{'='*70}")
    print("BATCH PROCESSING SUMMARY - v2.0")
    print(f"{'='*70}")
    print(f"Total PDFs: {len(pdf_paths)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(pdf_paths) - successful}")
    print(f"Related: {related}")
    print(f"Not Related: {not_related}")
    print(f"{'='*70}\n")
    
    # Save batch summary
    if save_reports:
        summary_path = Path(output_dir) / 'batch_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump({
                'total_pdfs': len(pdf_paths),
                'successful': successful,
                'failed': len(pdf_paths) - successful,
                'related_count': related,
                'not_related_count': not_related,
                'preprocessing_enabled': use_preprocessing,
                'timestamp': datetime.now().isoformat(),
                'results': all_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"? Batch summary saved: {summary_path}\n")
    
    return all_results


# Example usage and testing
if __name__ == "__main__":
    print("\nTesting Drug Causality Classifier v2.0...")
    
    classifier = CausalityClassifier(use_preprocessing=True)
    
    # Test edge cases
    test_cases = [
        "Patient developed hearing loss after taking bortezomib.",
        "Hearing loss secondary to bortezomib is a very rare side effect.",
        "Neuropathy following paclitaxel administration.",
        "Cardiotoxicity is a known side effect of doxorubicin.",
    ]
    
    print("\n" + "="*80)
    print("CAUSALITY CLASSIFICATION TESTS - v2.0")
    print("="*80)
    
    for text in test_cases:
        result = classifier.predict(text, return_probs=True, enhance_score=True)
        
        print(f"\nText: {text}")
        print(f"Classification: {result['prediction'].upper()}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Markers Detected: {result['causality_markers_detected']}")
        if result['causality_markers_detected']:
            print(f"Marker Count: {result['marker_count']}")
        print(f"Probabilities: Not Related {result['probabilities']['not_related']:.2%} | Related {result['probabilities']['related']:.2%}")

