"""
Comprehensive unit tests for Drug Causality BERT v2.0 components.
Zero-cost, local execution. Tests standardizers, extractors, calculators, and API fallbacks.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure UTF-8 output encoding for Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.clinical_standardizers import (
    MedDRAStandardizer,
    DrugExtractor,
    ADRExtractor,
    CaseInfoExtractor,
    calculate_naranjo_score,
    calculate_who_umc
)
from src.fda_connector import FDAFAERSConnector
from src.ollama_report_generator import OllamaReportGenerator
from src.inference import preprocess_medical_causality, detect_causality_markers, safe_sent_tokenize


class TestClinicalComponents(unittest.TestCase):

    def setUp(self):
        self.meddra = MedDRAStandardizer()
        self.drug_ext = DrugExtractor()
        self.adr_ext = ADRExtractor()
        self.case_ext = CaseInfoExtractor()

    def test_meddra_standardizer(self):
        self.assertEqual(self.meddra.standardize("hearing loss"), "Deafness")
        self.assertEqual(self.meddra.standardize("kidney injury"), "Acute kidney injury")
        self.assertEqual(self.meddra.standardize("hepatotoxicity"), "Hepatic necrosis")
        self.assertEqual(self.meddra.standardize("pruritus"), "Pruritus")
        self.assertEqual(self.meddra.standardize("uncommon rash"), "Rash")

    def test_drug_extractor(self):
        text = "The patient was prescribed bortezomib and cisplatin after failure on methotrexate and lisinopril."
        drugs = self.drug_ext.extract(text)
        self.assertIn("Bortezomib", drugs)
        self.assertIn("Cisplatin", drugs)
        self.assertIn("Methotrexate", drugs)
        self.assertIn("Lisinopril", drugs)

    def test_adr_extractor(self):
        text = "Patient suffered peripheral neuropathy, severe thrombocytopenia, and acute kidney damage."
        adrs = self.adr_ext.extract(text)
        self.assertIn("Peripheral Neuropathy", adrs)
        self.assertIn("Thrombocytopenia", adrs)
        self.assertIn("Nephrotoxicity", adrs)

    def test_case_info_extractor(self):
        text = "A 62-year-old male with a history of diabetes and hypertension presented with jaundice."
        demo = self.case_ext.extract_demographics(text)
        self.assertEqual(demo.get("age"), "62")
        self.assertEqual(demo.get("gender"), "Male")

        conditions = self.case_ext.extract_conditions(text)
        self.assertIn("Diabetes", conditions)
        self.assertIn("Hypertension", conditions)

    def test_naranjo_score(self):
        score, cat = calculate_naranjo_score(
            previous_conclusive_reports=True,
            adverse_event_after_drug=True,
            improved_on_discontinuation=True,
            reappeared_on_readministration=False,
            alternative_causes_excluded=True,
            confirmed_by_objective_evidence=True
        )
        self.assertGreaterEqual(score, 5)
        self.assertIn(cat, ["Probable", "Definite"])

    def test_who_umc_algorithm(self):
        cat = calculate_who_umc(
            temporal_relationship=True,
            dechallenge_positive=True,
            rechallenge_positive=True,
            alternative_causes_unlikely=True,
            plausible_pharmacology=True
        )
        self.assertEqual(cat, "Certain")

        cat_unlikely = calculate_who_umc(
            temporal_relationship=False,
            dechallenge_positive=False,
            rechallenge_positive=False,
            alternative_causes_unlikely=False,
            plausible_pharmacology=False
        )
        self.assertEqual(cat_unlikely, "Unlikely")

    def test_text_preprocessing_and_markers(self):
        raw = "Hearing loss secondary to bortezomib is a very rare side effect."
        processed = preprocess_medical_causality(raw)
        self.assertIn("caused by", processed)
        self.assertIn("is an adverse effect", processed)

        markers = detect_causality_markers(raw)
        self.assertTrue(markers["has_markers"])
        self.assertIn("secondary to", markers["markers_found"])

    def test_sentence_tokenization(self):
        paragraph = "Patient started medication on Monday. On Tuesday, acute nausea occurred! Symptoms subsided by Friday."
        sentences = safe_sent_tokenize(paragraph)
        self.assertEqual(len(sentences), 3)

    @patch("requests.get")
    def test_fda_connector_mock(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "safetyreportid": "12345",
                    "patient": {
                        "reaction": [
                            {"reactionmeddrapt": "Peripheral neuropathy", "reactionoutcome": "1"}
                        ]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        connector = FDAFAERSConnector()
        events = connector.get_adverse_events("bortezomib", limit=1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "Peripheral neuropathy")
        self.assertEqual(events[0]["outcome"], "Recovered/Resolved")

    def test_ollama_fallback_report(self):
        generator = OllamaReportGenerator(model_name="nonexistent:model")
        # Ensure that even if Ollama connection fails, it generates a complete fallback report
        report = generator.generate_drug_causality_report(
            drug_name="Bortezomib",
            adverse_event="Peripheral Neuropathy",
            causality_score=0.96,
            who_umc_result="Probable / Likely",
            naranjo_score=7,
            sentence_analysis=[{"text": "Patient developed neuropathy after 3 cycles of bortezomib.", "prediction": "related"}]
        )
        self.assertIn("CLINICAL DRUG CAUSALITY ASSESSMENT REPORT", report)
        self.assertIn("Bortezomib", report)
        self.assertIn("Peripheral Neuropathy", report)


if __name__ == "__main__":
    unittest.main()

