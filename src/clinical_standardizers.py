"""
Clinical Standardization & Pharmacovigilance Rules Engine
- MedDRA Preferred Term (PT) standardization
- Clinical Entity Extraction (Drugs, ADRs, Patient Demographics)
- WHO-UMC Causality Algorithm
- Naranjo Adverse Drug Reaction Probability Scale
Zero-cost, local deterministic implementation following international pharmacovigilance guidelines.
"""

import re
from typing import Dict, List, Set, Tuple


class MedDRAStandardizer:
    """
    Standardizes reported symptoms and adverse events to MedDRA Preferred Terms (PT).
    """

    def __init__(self):
        self.meddra_mapping = {
            "hearing loss": "Deafness",
            "deafness": "Deafness",
            "tinnitus": "Tinnitus",
            "neuropathy": "Neuropathy peripheral",
            "peripheral neuropathy": "Neuropathy peripheral",
            "nerve damage": "Neuropathy peripheral",
            "cardiotoxicity": "Cardiotoxicity",
            "heart failure": "Cardiac failure",
            "arrhythmia": "Arrhythmia",
            "myocardial infarction": "Myocardial infarction",
            "heart attack": "Myocardial infarction",
            "nephrotoxicity": "Acute kidney injury",
            "kidney injury": "Acute kidney injury",
            "renal failure": "Renal failure acute",
            "hepatotoxicity": "Hepatic necrosis",
            "liver failure": "Hepatic failure",
            "liver injury": "Drug-induced liver injury",
            "jaundice": "Jaundice",
            "thrombocytopenia": "Thrombocytopenia",
            "low platelets": "Thrombocytopenia",
            "anemia": "Anaemia",
            "neutropenia": "Neutropenia",
            "leukopenia": "Leukopenia",
            "nausea": "Nausea",
            "vomiting": "Vomiting",
            "diarrhea": "Diarrhoea",
            "rash": "Rash",
            "pruritus": "Pruritus",
            "itching": "Pruritus",
            "urticaria": "Urticaria",
            "hives": "Urticaria",
            "stevens-johnson": "Stevens-Johnson syndrome",
            "sjs": "Stevens-Johnson syndrome",
            "toxic epidermal necrolysis": "Toxic epidermal necrolysis",
            "anaphylaxis": "Anaphylactic reaction",
            "angioedema": "Angioedema",
            "pancreatitis": "Pancreatitis acute",
            "hypotension": "Hypotension",
            "hypertension": "Hypertension",
            "headache": "Headache",
            "dizziness": "Dizziness",
            "fatigue": "Fatigue",
            "seizure": "Seizure",
            "convulsion": "Seizure"
        }

    def standardize(self, adr_text: str) -> str:
        """Map text or subphrase to standard MedDRA Preferred Term."""
        if not adr_text:
            return "Unspecified Event"
        clean = adr_text.lower().strip()
        for phrase, pt in self.meddra_mapping.items():
            if phrase in clean:
                return pt
        return adr_text.strip().title()


class DrugExtractor:
    """
    Extracts suspected drugs and concomitant medications from clinical text
    using recognized therapeutic names, brand names, and pharmacological suffix patterns.
    """

    COMMON_DRUGS = {
        # Oncology & Immunotherapy
        "bortezomib": ["bortezomib", "velcade"],
        "methotrexate": ["methotrexate", "mtx", "trexall"],
        "cisplatin": ["cisplatin", "platinol"],
        "paclitaxel": ["paclitaxel", "taxol"],
        "doxorubicin": ["doxorubicin", "adriamycin"],
        "rituximab": ["rituximab", "rituxan"],
        "pembrolizumab": ["pembrolizumab", "keytruda"],
        "nivolumab": ["nivolumab", "opdivo"],
        "cyclophosphamide": ["cyclophosphamide", "cytoxan"],
        "fluorouracil": ["fluorouracil", "5-fu"],
        # Cardiovascular & Metabolic
        "metoprolol": ["metoprolol", "lopressor", "toprol"],
        "simvastatin": ["simvastatin", "zocor"],
        "atorvastatin": ["atorvastatin", "lipitor"],
        "lisinopril": ["lisinopril", "prinivil", "zestril"],
        "amiodarone": ["amiodarone", "cordarone"],
        "metformin": ["metformin", "glucophage"],
        "warfarin": ["warfarin", "coumadin"],
        "aspirin": ["aspirin", "acetylsalicylic acid", "asa"],
        # Antimicrobial & Antiviral
        "amoxicillin": ["amoxicillin", "amoxil"],
        "ciprofloxacin": ["ciprofloxacin", "cipro"],
        "vancomycin": ["vancomycin", "vancocin"],
        "gentamicin": ["gentamicin", "garamycin"],
        "azithromycin": ["azithromycin", "zithromax"],
        # Analgesics & Anti-inflammatory
        "ibuprofen": ["ibuprofen", "advil", "motrin"],
        "acetaminophen": ["acetaminophen", "paracetamol", "tylenol"],
        "morphine": ["morphine"],
        "fentanyl": ["fentanyl"],
    }

    # Pharmacological stem regex patterns (USAN/INN stems)
    STEM_PATTERNS = [
        re.compile(r"\b([a-z]+(?:mab|nib|cept|pril|statin|sartan|olol|cillin|mycin|floxacin|dipine|prazole|tidine|parin|glitazone|grel))\b", re.IGNORECASE)
    ]

    def extract(self, text: str) -> Set[str]:
        """Extract set of identified drug names."""
        if not text:
            return set()
        text_lower = text.lower()
        found = set()

        # Dictionary matching
        for canonical, aliases in self.COMMON_DRUGS.items():
            for alias in aliases:
                if re.search(rf"\b{re.escape(alias)}\b", text_lower):
                    found.add(canonical.capitalize())
                    break

        # Suffix/INN stem matching
        for pattern in self.STEM_PATTERNS:
            for match in pattern.finditer(text):
                candidate = match.group(1).lower()
                # Exclude common non-drug English words
                if candidate not in {"action", "fraction", "reaction", "friction", "motion", "section"}:
                    found.add(candidate.capitalize())

        return found

    def get_frequencies(self, text: str) -> Dict[str, int]:
        """Return mention frequency count for identified drugs."""
        found = self.extract(text)
        text_lower = text.lower()
        freqs = {}
        for drug in found:
            count = len(re.findall(rf"\b{re.escape(drug.lower())}\b", text_lower))
            if count > 0:
                freqs[drug] = count
        return freqs


class ADRExtractor:
    """
    Identifies reported Adverse Drug Reactions (ADRs) from clinical text.
    """

    ADR_KEYWORDS = {
        "hearing loss": ["hearing loss", "deafness", "tinnitus", "hypoacusis"],
        "peripheral neuropathy": ["neuropathy", "nerve damage", "paresthesia", "numbness"],
        "cardiotoxicity": ["cardiotoxicity", "heart failure", "cardiomyopathy", "arrhythmia"],
        "nephrotoxicity": ["nephrotoxicity", "kidney damage", "renal failure", "creatinine elevation"],
        "hepatotoxicity": ["hepatotoxicity", "liver injury", "hepatic necrosis", "elevated alt", "elevated ast"],
        "thrombocytopenia": ["thrombocytopenia", "low platelets", "petechiae"],
        "anemia": ["anemia", "low hemoglobin", "pale"],
        "gastrointestinal distress": ["nausea", "vomiting", "diarrhea", "abdominal pain"],
        "cutaneous reaction": ["rash", "pruritus", "urticaria", "hives", "erythema", "blisters"],
        "severe cutaneous adverse reaction": ["stevens-johnson", "sjs", "toxic epidermal necrolysis", "ten", "dress syndrome"],
        "anaphylaxis": ["anaphylaxis", "anaphylactic", "angioedema", "bronchospasm"],
        "neurological symptoms": ["seizure", "convulsion", "confusion", "ataxia", "tremor"]
    }

    def extract(self, text: str) -> Set[str]:
        """Extract reported adverse events."""
        if not text:
            return set()
        text_lower = text.lower()
        found = set()
        for canonical, terms in self.ADR_KEYWORDS.items():
            for term in terms:
                if re.search(rf"\b{re.escape(term)}\b", text_lower):
                    found.add(canonical.title())
                    break
        return found


class CaseInfoExtractor:
    """
    Extracts patient demographics and concurrent conditions from case reports.
    """

    def extract_demographics(self, text: str) -> Dict[str, str]:
        info = {}
        if not text:
            return info
        age_match = re.search(r"(\d{1,3})\s*(?:year[s]?-old|yo|y\.o\.|-year-old|years of age)", text, re.IGNORECASE)
        if age_match:
            info["age"] = age_match.group(1)
        gender_match = re.search(r"\b(male|female|man|woman|boy|girl)\b", text, re.IGNORECASE)
        if gender_match:
            val = gender_match.group(1).lower()
            info["gender"] = "Male" if val in {"male", "man", "boy"} else "Female"
        return info

    def extract_conditions(self, text: str) -> List[str]:
        conditions = []
        if not text:
            return conditions
        keywords = [
            "diabetes", "hypertension", "cancer", "carcinoma", "lymphoma", "myeloma",
            "leukemia", "infection", "sepsis", "renal failure", "cirrhosis", "hepatitis",
            "heart failure", "coronary artery disease", "copd", "asthma", "stroke"
        ]
        text_lower = text.lower()
        for cond in keywords:
            if re.search(rf"\b{re.escape(cond)}\b", text_lower):
                conditions.append(cond.title())
        return list(dict.fromkeys(conditions))


def calculate_naranjo_score(
    previous_conclusive_reports: bool = True,
    adverse_event_after_drug: bool = True,
    improved_on_discontinuation: bool = True,
    reappeared_on_readministration: bool = False,
    alternative_causes_excluded: bool = True,
    reaction_with_placebo: bool = False,
    drug_detected_in_toxic_levels: bool = False,
    reaction_more_severe_increased_dose: bool = False,
    similar_reaction_in_past: bool = False,
    confirmed_by_objective_evidence: bool = True
) -> Tuple[int, str]:
    """
    Calculates the Naranjo Adverse Drug Reaction Probability Scale score (0 to 13).
    Returns (score, category).
    Categories:
    - >= 9: Definite
    - 5 - 8: Probable
    - 1 - 4: Possible
    - <= 0: Doubtful
    """
    score = 0
    score += 1 if previous_conclusive_reports else 0
    score += 2 if adverse_event_after_drug else -1
    score += 1 if improved_on_discontinuation else 0
    score += 2 if reappeared_on_readministration else -1
    score += 2 if alternative_causes_excluded else -1
    score += -1 if reaction_with_placebo else 1
    score += 1 if drug_detected_in_toxic_levels else 0
    score += 1 if reaction_more_severe_increased_dose else 0
    score += 1 if similar_reaction_in_past else 0
    score += 1 if confirmed_by_objective_evidence else 0

    if score >= 9:
        cat = "Definite"
    elif score >= 5:
        cat = "Probable"
    elif score >= 1:
        cat = "Possible"
    else:
        cat = "Doubtful"

    return score, cat


def calculate_who_umc(
    temporal_relationship: bool,
    dechallenge_positive: bool,
    rechallenge_positive: bool,
    alternative_causes_unlikely: bool,
    plausible_pharmacology: bool
) -> str:
    """
    Determines WHO-UMC causality category:
    - Certain
    - Probable / Likely
    - Possible
    - Unlikely
    - Conditional / Unclassified
    - Unassessable / Unclassifiable
    """
    if temporal_relationship and dechallenge_positive and rechallenge_positive and alternative_causes_unlikely and plausible_pharmacology:
        return "Certain"
    elif temporal_relationship and dechallenge_positive and alternative_causes_unlikely:
        return "Probable / Likely"
    elif temporal_relationship and plausible_pharmacology:
        return "Possible"
    elif not temporal_relationship:
        return "Unlikely"
    else:
        return "Conditional / Unclassified"

