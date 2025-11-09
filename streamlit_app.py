import streamlit as st
from src.ollama_report_generator import OllamaReportGenerator

MODEL_OPTIONS = {
    "Llama 3.2 (3B)": "llama3.2:3b",
    "Meditron 7B": "meditron:7b",
    "Mistral 7B": "mistral:7b",
}

st.set_page_config(page_title="Drug Causality BERT V2.0", layout="wide")
st.title("💊 Drug Causality BERT V2.0")

st.caption("Advanced BioBERT-based system for automated drug-adverse event causality assessment with regulatory report generation capabilities.")

# Instructions or help tab can be expanded here as needed

tab1, tab2, tab3, tab4 = st.tabs([
    "Single Text",
    "PDF Analysis",
    "Batch Processing",
    "Instructions / About",
])

with tab1:
    st.header("Single Statement Causality Classification")
    text_input = st.text_area("Enter a single drug-event clinical sentence", "")
    threshold = st.slider("Classification threshold", 0.3, 0.9, 0.5, step=0.01)
    st.caption("Recommended: 0.3–0.4 (sensitive), 0.5 (balanced), 0.7–0.8 (precise)")
    # Ollama model dropdown just below threshold
    model_choice = st.selectbox("Select Ollama Model for Clinical Report Generation", list(MODEL_OPTIONS.keys()), key="tab1_model")
    model_name = MODEL_OPTIONS[model_choice]
    if st.button("Classify"):
        st.write("Your text would be analyzed here. (Demo placeholder)")

with tab2:
    st.header("PDF Analysis")
    pdf_file = st.file_uploader("Upload a medical case report PDF", type=["pdf"])
    threshold = st.slider("Classification threshold", 0.3, 0.9, 0.5, step=0.01, key="pdf_threshold")
    st.caption("Recommended: 0.3–0.4 (sensitive), 0.5 (balanced), 0.7–0.8 (precise)")
    # Ollama model dropdown just below threshold (PDF tab)
    model_choice_2 = st.selectbox("Select Ollama Model for Clinical Report Generation", list(MODEL_OPTIONS.keys()), key="tab2_model")
    model_name_2 = MODEL_OPTIONS[model_choice_2]
    if pdf_file is not None:
        st.write("PDF received. (Insert PDF processing logic here)")
        st.session_state["extracted_data"] = {
            "drug": "Demo Drug",
            "adverse_event": "Demo Event",
            "confidence": 0.87,
            "who_umc_result": "Probable",
            "naranjo_score": 7,
            "sentences": [
                {"text": "Patient developed GI symptoms after Demo Drug.", "prediction": "related"}
            ],
        }
        if st.button("Generate Clinical Report from PDF"):
            ollama_gen = OllamaReportGenerator(model_name=model_name_2)
            report = ollama_gen.generate_drug_causality_report(
                drug_name="Demo Drug",
                adverse_event="Demo Event",
                causality_score=0.87,
                who_umc_result="Probable",
                naranjo_score=7,
                sentence_analysis=[
                    {"text": "Patient developed GI symptoms after Demo Drug.", "prediction": "related"}
                ]
            )
            st.markdown(report)
            st.download_button("Download Clinical Report", data=report, file_name="clinical_report.md")
    else:
        st.info("Please upload a medical case report PDF.")

with tab3:
    st.header("Batch Processing (Coming Soon)")
    st.warning("Batch PDF analysis is under construction for the public demo.")

with tab4:
    st.header("Instructions & About")
    st.markdown("""
    1. **Single Text:** Quickly classify an individual statement for drug-event causality.
    2. **PDF Analysis:** Upload medical case reports for full document processing.
    3. **Threshold:** Adjust to balance between sensitivity and specificity.
    4. **Model Selection:** Use the dropdown below the threshold slider on each tab to pick your local LLM for clinical report generation.
    5. **Local LLMs:** This app runs reports **100% offline** with your local Ollama install (no API keys required).
    6. **Contact & Support:** See GitHub repo for issue submission or documentation.
    """)

st.markdown("> **Switch between multiple local LLMs for report style, privacy, and accuracy.**")
