import streamlit as st
from src.ollama_report_generator import OllamaReportGenerator
import PyPDF2

MODEL_OPTIONS = {
    "Llama 3.2 (3B)": "llama3.2:3b",
    "Meditron 7B": "meditron:7b",
    "Mistral 7B": "mistral:7b",
}

st.set_page_config(page_title="Drug Causality BERT V2.0", layout="wide")
st.title("💊 Drug Causality BERT V2.0")
st.caption("Advanced BioBERT-based system for automated drug-adverse event causality assessment with regulatory report generation capabilities.")

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

    # Ollama model dropdown integrated below threshold
    model_choice = st.selectbox("Select Ollama Model for Clinical Report Generation", list(MODEL_OPTIONS.keys()), key="tab1_model")
    model_name = MODEL_OPTIONS[model_choice]

    if st.button("Classify"):
        st.write("Classification not implemented in this demo.")

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

        # TODO: Replace with your actual NLP extraction methods
        extracted_drugs = ["Aspirin", "Paracetamol"]
        extracted_events = ["Headache", "Nausea", "Dizziness"]
        st.session_state['extracted_drugs'] = extracted_drugs
        st.session_state['extracted_events'] = extracted_events

        drug_choice = st.selectbox("Select Drug", st.session_state['extracted_drugs'])
        event_choice = st.selectbox("Select Adverse Event", st.session_state['extracted_events'])

        if st.button("Generate Clinical Report from PDF"):
            ollama_gen = OllamaReportGenerator(model_name=model_name_2)
            report = ollama_gen.generate_drug_causality_report(
                drug_name=drug_choice,
                adverse_event=event_choice,
                causality_score=0.87,  # Replace with actual scoring from your analysis
                who_umc_result="Probable",
                naranjo_score=7,
                sentence_analysis=[{"text": "Sample sentence from report", "prediction": "related"}]
            )
            st.markdown(report)
            st.download_button("Download Clinical Report", data=report, file_name="clinical_report.md")

    else:
        st.info("Please upload a medical case report PDF.")

with tab3:
    st.header("Batch Processing (Coming Soon)")
    st.warning("Batch PDF analysis is under construction for this demo.")

with tab4:
    st.header("Instructions & About")
    st.markdown("""
    - Upload PDFs on the PDF Analysis tab.
    - Adjust classification thresholds to tune sensitivity.
    - Select local Ollama model for report generation.
    - This app runs reports 100% offline using local Ollama models; no cloud API involved.
    """)

st.markdown("> **Switch between multiple local LLMs for report style, privacy, and accuracy.**")
