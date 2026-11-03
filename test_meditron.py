"""
Test script for Ollama local report generation.
Supports Meditron-7B, Llama-3.2, and fallback template generation.
"""

import sys
import os

# Ensure UTF-8 output encoding for Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.ollama_report_generator import OllamaReportGenerator

def test_generator():
    print("[1/3] Initializing Ollama Report Generator (Meditron-7B)...")
    generator = OllamaReportGenerator(model_name="meditron:7b")

    print("[2/3] Testing local Ollama connection...")
    is_connected = generator.test_connection()
    if is_connected:
        print("[OK] Ollama is running and accessible!")
    else:
        print("[INFO] Local Ollama server is not running (Run 'ollama serve' to enable LLM generation).")
        print("[INFO] Demonstrating zero-cost deterministic fallback report generation...")

    print("\n[3/3] Generating drug causality clinical report...")
    report = generator.generate_drug_causality_report(
        drug_name="Aspirin",
        adverse_event="Gastrointestinal bleeding",
        causality_score=0.89,
        who_umc_result="Probable",
        naranjo_score=7,
        sentence_analysis=[
            {'text': 'Patient developed bleeding 2 days after starting aspirin.', 'prediction': 'related'},
            {'text': 'No prior history of GI issues.', 'prediction': 'related'},
            {'text': 'Symptoms resolved after discontinuation.', 'prediction': 'related'}
        ],
        faers_data={'total_reports': 1234}
    )

    print("\n" + "=" * 60)
    print("GENERATED REPORT PREVIEW:")
    print("=" * 60)
    print(report[:450] + "\n...")
    print("=" * 60)
    print("[SUCCESS] Report generation completed without error!")

if __name__ == "__main__":
    test_generator()
