"""
Drug Causality BERT v2.0 - PART 1: Core Classification & Configuration
"""

import streamlit as st
import torch
import re
from typing import Dict
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ===== MEDICAL TEXT PREPROCESSING =====

def preprocess_medical_causality(text: str) -> str:
    text_lower = text.lower()
    replacements = {
        'secondary to': 'caused by',
        'due to': 'caused by',
        'induced by': 'caused by',
        'is a very rare side effect': 'is an adverse effect',
        'is a rare side effect': 'is an adverse effect',
        'is a common side effect': 'is an adverse effect',
        'may be related to': 'related to',
        'possibly related to': 'related to',
        'likely related to': 'related to',
        'following administration': 'following',
        'after taking': 'following',
    }
    for old, new in replacements.items():
        text_lower = text_lower.replace(old, new)
    return text_lower

def detect_causality_markers(text: str) -> Dict:
    markers = [
        'secondary to', 'caused by', 'induced by', 'due to', 'following',
        'side effect', 'adverse effect', 'related to', 'associated with',
    ]
    text_lower = text.lower()
    found = [m for m in markers if m in text_lower]
    return {
        'has_markers': len(found) > 0,
        'markers': found,
        'count': len(found)
    }

# ===== CLASSIFICATION FUNCTION =====

@st.cache_resource
def load_model():
    try:
        model_path = "./models/production_model_final"
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        return tokenizer, model
    except:
        st.error("Model not found in ./models/production_model_final")
        return None, None

def classify_causality(text: str, threshold: float, enhance_scores: bool) -> Dict:
    tokenizer, model = load_model()
    if tokenizer is None:
        return None
    
    model.eval()
    
    preprocessed = preprocess_medical_causality(text)
    markers = detect_causality_markers(text)
    
    inputs = tokenizer(preprocessed, return_tensors="pt", truncation=True, padding=True, max_length=96)
    
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1).numpy()[0]
    
    base_score = float(probs[1])
    
    if enhance_scores and markers['has_markers']:
        boost = min(0.15, markers['count'] * 0.05)
        final_score = min(base_score + boost, 0.99)
    else:
        final_score = base_score
    
    prediction = 'RELATED' if final_score > threshold else 'NOT RELATED'
    
    return {
        'prediction': prediction,
        'confidence': final_score,
        'base_score': base_score,
        'markers': markers,
        'probabilities': {
            'not_related': float(probs[0]),
            'related': float(probs[1])
        }
    }

# ===== PAGE SETUP =====

st.set_page_config(
    page_title="Drug Causality BERT v2.0",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("<h1>💊 Drug Causality BERT v2.0</h1>", unsafe_allow_html=True)
st.markdown("**BioBERT-based Pharmacovigilance System | F1: 0.9759 | PBRER/PSUR Compliant**")
st.divider()
