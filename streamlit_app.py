import streamlit as st
from src.ollama_report_generator import OllamaReportGenerator

MODEL_OPTIONS = {
    "Llama 3.2 (3B)": "llama3.2:3b",
    "Meditron 7B": "meditron:7b",
    "Mistral 7B": "mistral:7b",
}

st.header("🤖 AI-Powered Clinical Report Generator")

model_choice = st.selectbox("Select Ollama Model", list(MODEL_OPTIONS.keys()))
model_name = MODEL_OPTIONS[model_choice]

@st.cache_resource(hash_funcs={OllamaReportGenerator: lambda _: None})
def get_ollama_gen(model_name):
    return OllamaReportGenerator(model_name=model_name)

ollama_gen = get_ollama_gen(model_name)

if st.session_state.get("extracted_data"):
    data = st.session_state["extracted_data"]
    if st.button(f"Generate Clinical Report with {model_choice}"):
        with st.spinner(f"Generating report with {model_choice}..."):
            report = ollama_gen.generate_drug_causality_report(
                drug_name=data.get("drug", "N/A"),
                adverse_event=data.get("adverse_event", "N/A"),
                causality_score=data.get("confidence", 0.0),
                who_umc_result=data.get("who_umc_result", "Unknown"),
                naranjo_score=data.get("naranjo_score", 0),
                sentence_analysis=data.get("sentences", []),
            )
            st.markdown(report)
            st.download_button(
                "Download Clinical Report",
                report,
                file_name=f"clinical_report_{data['drug']}_{model_choice.replace(' ', '_')}.md",
                mime="text/markdown",
            )
else:
    st.info("Please upload and analyze a PDF document to generate reports.")

st.caption("Switch between multiple local LLMs for report style, privacy, and accuracy.")
