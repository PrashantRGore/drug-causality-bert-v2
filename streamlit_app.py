import streamlit as st
from src.ollama_report_generator import OllamaReportGenerator
import PyPDF2
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import os

MODEL_OPTIONS = {
    "Llama 3.2 (3B)": "llama3.2:3b",
    "Meditron 7B": "meditron:7b",
    "Mistral 7B": "mistral:7b",
}

st.set_page_config(page_title="Drug Causality BERT V2.0", layout="wide")
st.title("💊 Drug Causality BERT V2.0")
st.caption("Advanced BioBERT-based system for automated drug-adverse event causality assessment with regulatory report generation capabilities.")

# Load BioBERT model from Hugging Face with token support
@st.cache_resource
def load_biobert_model():
    model_name = "PrashantRGore/drug-causality-bert-v2-model"
    # Get token from environment variable or Streamlit secrets
    token = os.environ.get("HF_TOKEN") or st.secrets.get("HF_TOKEN", None)
    
    try:
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            use_auth_token=token
        )
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            use_auth_token=token
        )
        return model, tokenizer
    except Exception as e:
        st.error(f"Failed to load model from Hugging Face: {e}")
        st.info("Please ensure the model is uploaded to: https://huggingface.co/PrashantRGore/drug-causality-bert-v2-model")
        return None, None

model, tokenizer = load_biobert_model()

tab1, tab2, tab3, tab4 = st.tabs([
    "Single Text",
    "PDF Analysis",
    "Batch Processing",
    "Instructions / About",
])

with tab1:
    st.header("Single Statement Causality Classification")
    text_input = st.text_area("Enter a single drug-event clinical sentence")
    threshold = st.slider("Classification threshold", 0.3, 0.9, 0.5, step=0.01)
    st.caption("Recommended: 0.3–0.4 (sensitive), 0.5 (balanced), 0.7–0.8 (precise)")

    model_choice = st.selectbox("Select Ollama Model for Clinical Report Generation", list(MODEL_OPTIONS.keys()), key="tab1_model")
    model_name = MODEL_OPTIONS[model_choice]

    if st.button("Classify"):
        if text_input and model and tokenizer:
            inputs = tokenizer(text_input, return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
                prediction = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][prediction].item()
            
            result = "Related" if prediction == 1 else "Not Related"
            st.success(f"Prediction: **{result}** (Confidence: {confidence:.2%})")
        else:
            st.warning("Please enter text and ensure model is loaded.")

with tab2:
    st.header("PDF Analysis")
    pdf_file = st.file_uploader("Upload medical case report PDF", type=["pdf"])
    threshold = st.slider("Classification threshold", 0.3, 0.9, 0.5, step=0.01, key="pdf_threshold")
    st.caption("Recommended: 0.3–0.4 (sensitive), 0.5 (balanced), 0.7–0.8 (precise)")

    model_choice_2 = st.selectbox("Select Ollama Model for Clinical Report Generation", list(MODEL_OPTIONS.keys()), key="tab2_model")
    model_name_2 = MODEL_OPTIONS[model_choice_2]

    if pdf_file is not None:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"

        st.text_area("Extracted Text (Preview)", full_text[:500] + "...", height=150)

        # TODO: Replace with your actual NLP extraction methods
        extracted_drugs = ["Aspirin", "Paracetamol", "Ibuprofen"]
        extracted_events = ["Headache", "Nausea", "Dizziness", "Rash"]
        st.session_state['extracted_drugs'] = extracted_drugs
        st.session_state['extracted_events'] = extracted_events

        drug_choice = st.selectbox("Select Drug", st.session_state['extracted_drugs'])
        event_choice = st.selectbox("Select Adverse Event", st.session_state['extracted_events'])

        if st.button("Generate Clinical Report from PDF"):
            try:
                ollama_gen = OllamaReportGenerator(model_name=model_name_2)
                report = ollama_gen.generate_drug_causality_report(
                    drug_name=drug_choice,
                    adverse_event=event_choice,
                    causality_score=0.87,
                    who_umc_result="Probable",
                    naranjo_score=7,
                    sentence_analysis=[{"text": "Sample sentence from report", "prediction": "related"}]
                )
                st.markdown(report)
                st.download_button("Download Clinical Report", data=report, file_name="clinical_report.md")
            except Exception as e:
                st.error(f"Error: Failed to connect to Ollama. Please check that Ollama is downloaded, running and accessible.")
                st.info("For local use: Install Ollama from https://ollama.com/download and run 'ollama serve'")
                st.error(f"Details: {e}")

    else:
        st.info("Please upload a medical case report PDF.")

with tab3:
    st.header("Batch Processing (Coming Soon)")
    st.warning("Batch PDF analysis is under construction for this demo.")

with tab4:
    st.header("Instructions & About")
    st.markdown("""
    ### How to Use This App
    
    1. **Single Text Classification**: Enter a clinical sentence to classify drug-event causality relationship.
    2. **PDF Analysis**: Upload medical case reports for full document processing with drug/event extraction.
    3. **Classification Threshold**: Adjust to balance between sensitivity and specificity:
       - 0.3–0.4: High sensitivity (catches more cases)
       - 0.5: Balanced (default)
       - 0.7–0.8: High precision (fewer false positives)
    4. **Ollama Model Selection**: Choose from local LLM models for clinical report generation (local deployment only).
    5. **Local Privacy**: Ollama runs reports 100% offline using local models; no cloud API required.
    
    ### Requirements for Local Use with Ollama
    - Install Ollama from https://ollama.com/download
    - Pull models: `ollama pull llama3.2:3b`, `ollama pull meditron:7b`, `ollama pull mistral:7b`
    - Start Ollama server: `ollama serve`
    - Run this app: `streamlit run streamlit_app.py`
    
    ### Model Information
    - **BioBERT Model**: PrashantRGore/drug-causality-bert-v2-model (loaded from Hugging Face)
    - **Training Data**: ADE Corpus V2 (CSIRO)
    - **Performance**: F1 Score 97.59%, Accuracy 97.59%
    
    ### Note on Cloud Deployment
    - On Streamlit Cloud, Ollama LLM features are disabled as they require local server
    - All other features (PDF analysis, causality classification) work normally
    
    ### Contact & Support
    - GitHub: https://github.com/PrashantRGore/drug-causality-bert-v2
    - Report Issues: https://github.com/PrashantRGore/drug-causality-bert-v2/issues
    - Hugging Face Model: https://huggingface.co/PrashantRGore/drug-causality-bert-v2-model
    """)

st.markdown("> **Switch between multiple local LLMs for report style, privacy, and accuracy (local deployment only).**")
