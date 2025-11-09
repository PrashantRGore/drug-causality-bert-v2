import ollama
from typing import Dict, List
from datetime import datetime

class OllamaReportGenerator:
    def __init__(self, model_name="llama3.2:3b"):
        self.model_name = model_name
        self.client = ollama

    def set_model(self, model_name):
        self.model_name = model_name

    def generate_drug_causality_report(
        self, 
        drug_name: str,
        adverse_event: str,
        causality_score: float,
        who_umc_result: str,
        naranjo_score: int,
        sentence_analysis: List[Dict],
        faers_data: Dict = None
    ) -> str:
        related_sentences = [
            s.get("text", "") for s in sentence_analysis 
            if s.get("prediction") == "related"
        ][:3]
        naranjo_cat = "Definite" if naranjo_score >= 9 else "Probable" if naranjo_score >= 5 else "Possible"
        prompt = f"""Write a professional Drug Causality Event Report for:

Drug: {drug_name}
Adverse Event: {adverse_event}
Causality: {causality_score:.0%} confidence, WHO-UMC {who_umc_result}, Naranjo {naranjo_score} ({naranjo_cat})

Evidence: {'; '.join(related_sentences) if related_sentences else 'Clinical observation'}

Include sections: Executive Summary, Case Description, Causality Assessment, Clinical Recommendation, Conclusion. Use medical terminology."""
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={"temperature": 0.3, "num_predict": 1000}
            )
            return response["response"]
        except Exception as e:
            return f"Error: {e}\nEnsure Ollama is running: ollama serve"

    def generate_pbrer_section_11(
        self,
        drug_name: str,
        adverse_events: List[Dict],
        analysis_period: str = None
    ) -> str:
        period = analysis_period or "2025"
        events_text = '\\n'.join([
            f"- {e.get('name', 'Unknown')}: {e.get('causality', 'Unknown')} ({e.get('count', 0)} cases)"
            for e in adverse_events[:5]
        ])
        prompt = f"""Generate a PBRER Section 11 Summary for {drug_name} covering {period}.

Events analyzed: {len(adverse_events)}
{events_text}

Include: Summary of Significant Findings, Adverse Event Analysis, Causality Summary, Benefit-Risk Assessment. Follow ICH E2C(R2) guidelines."""
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={"temperature": 0.2, "num_predict": 1200}
            )
            return response["response"]
        except Exception as e:
            return f"Error: {e}"

    def test_connection(self) -> bool:
        try:
            self.client.generate(model=self.model_name, prompt="Test", options={"num_predict": 5})
            return True
        except:
            return False
