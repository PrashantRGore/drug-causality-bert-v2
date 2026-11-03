"""
FDA FAERS Connector for Pharmacovigilance Signal Verification
Queries the U.S. FDA OpenFDA API (public domain, free, no API key required).
Zero cost, official regulatory drug safety data.
"""

from typing import Dict, List, Optional
import requests


class FDAFAERSConnector:
    """
    Connects to the U.S. FDA OpenFDA Drug Adverse Event Reporting System (FAERS).
    Provides real-world adverse drug reaction frequencies and outcomes.
    """

    def __init__(self, timeout: int = 8):
        self.api_url = "https://api.fda.gov/drug/event.json"
        self.timeout = timeout

    def get_adverse_events(self, drug_name: str, limit: int = 10) -> List[Dict]:
        """
        Query OpenFDA for reported adverse events associated with a generic or brand drug name.
        Returns a list of event dictionaries with MedDRA Preferred Terms and reported outcomes.
        """
        if not drug_name or not drug_name.strip():
            return []

        clean_drug = drug_name.strip().lower()
        # Search against openfda generic name, medicinal product, and brand name
        query = f'(patient.drug.openfda.generic_name:"{clean_drug}"+patient.drug.medicinalproduct:"{clean_drug}")'
        params = {
            "search": query,
            "limit": limit
        }

        try:
            response = requests.get(self.api_url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                events = []
                for report in data.get("results", []):
                    patient = report.get("patient", {})
                    reactions = patient.get("reaction", [])
                    for reaction in reactions:
                        events.append({
                            "event": reaction.get("reactionmeddrapt", "Unspecified"),
                            "outcome": self._map_outcome(reaction.get("reactionoutcome", "Unknown")),
                            "safety_report_id": report.get("safetyreportid", "N/A")
                        })
                return events
            return []
        except Exception:
            # Graceful network degradation - never break user interface
            return []

    def get_event_frequency(self, drug_name: str, adverse_event: str) -> Dict:
        """
        Query specific co-occurrence frequency for a drug and an adverse event in FAERS.
        """
        if not drug_name or not adverse_event:
            return {"total_reports": 0, "available": False}

        clean_drug = drug_name.strip().lower()
        clean_event = adverse_event.strip().lower()
        query = f'patient.drug.openfda.generic_name:"{clean_drug}"+AND+patient.reaction.reactionmeddrapt:"{clean_event}"'
        params = {
            "search": query,
            "count": "patient.reaction.reactionmeddrapt.exact"
        }

        try:
            response = requests.get(self.api_url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                total = sum(r.get("count", 0) for r in results)
                return {"total_reports": total, "available": True, "breakdown": results[:5]}
            return {"total_reports": 0, "available": False}
        except Exception:
            return {"total_reports": 0, "available": False}

    @staticmethod
    def _map_outcome(outcome_code: str) -> str:
        """Map FDA numerical outcome code to ICH human-readable term."""
        mapping = {
            "1": "Recovered/Resolved",
            "2": "Recovering/Resolving",
            "3": "Not Recovered/Not Resolved",
            "4": "Recovered/Resolved with Sequelae",
            "5": "Fatal",
            "6": "Unknown"
        }
        return mapping.get(str(outcome_code), str(outcome_code))

