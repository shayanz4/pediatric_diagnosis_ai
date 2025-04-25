from pyswip import Prolog
from typing import List, Dict, Tuple, Optional

class DiagnosisEngine:
    def __init__(self, mode: str = "normal"):
        self.prolog = Prolog()
        self.mode = mode
        # Load KB according to mode
        if mode == "normal":
            self.prolog.consult("diagnosis.pl")
        else:  # dcg mode
            self.prolog.consult("dcg_rules.pl")
        self._reset_state()

    def _reset_state(self):
        """Reset all Prolog state between diagnoses"""
        self.prolog.query("retractall(user_response(_, _)).")
        self.prolog.query("retractall(has_symptom(_, _)).")

    def process_natural_language(self, text: str) -> List[str]:
        if self.mode == "dcg":
            # Use DCG parsing for DCG mode
            safe_text = text.replace('"', '\\"')
            query = f'parse_symptoms("{safe_text}", S)'
            try:
                result = list(self.prolog.query(query, maxresult=1))
                return result[0]["S"] if result else []
            except Exception as e:
                print(f"DCG parsing error: {e}")
                return []
        else:
            # For normal mode, simply split on comma or space as a simple heuristic.
            words = [w.strip() for w in text.replace(",", " ").split() if w.strip()]
            # Only return those that are in T1 (your predefined Tier‑1 symptoms)
            return [w for w in words if w in T1]

    def add_symptom(self, symptom: str, tier: int = 1):
        """Add a symptom with its tier to the Prolog KB"""
        try:
            self.prolog.assertz(f"has_symptom({symptom},{tier})")
        except Exception as e:
            print(f"Error adding symptom {symptom}: {e}")

    def add_response(self, key: str, value: str):
        """Add a user response to the Prolog KB"""
        try:
            safe_value = value.replace("'", "''")  # Escape single quotes for Prolog
            self.prolog.assertz(f"user_response({key},'{safe_value}')")
        except Exception as e:
            print(f"Error adding response {key}: {e}")

    def get_diagnosis(self) -> Tuple[List[Dict], Optional[str]]:
        """Get diagnosis results based on symptoms and responses"""
        try:
            diagnoses = [d["Disease"] for d in self.prolog.query("diagnosis(Disease).")]
            # Filter and calculate based on RULE_LEN
            diagnoses = [d for d in diagnoses if d in RULE_LEN]
            if not diagnoses:
                return [], None
            total = sum(RULE_LEN.get(d, 1) for d in diagnoses)
            results = []
            for d in diagnoses:
                probability = RULE_LEN.get(d, 1) * 100 / total
                results.append({
                    "disease": d.replace('_', ' ').title(),
                    "probability": round(probability, 1)
                })
            best = max(diagnoses, key=lambda d: RULE_LEN.get(d, 0))
            department = DEPT.get(best, "General Pediatrics")
            return results, department
        except Exception as e:
            print(f"Diagnosis error: {e}")
            return [], None

# Predefined mode‐independent constants
T1 = ["fever", "cough", "rash", "vomiting", "diarrhea", "runny_nose", "fatigue"]

T2 = {
    "fever": ["Describe the fever (low-grade / high-grade / intermittent):"],
    "cough": ["Type of cough (dry / productive / wheezing):"],
    "rash": ["Describe the rash (localized / widespread / itchy):"],
    "vomiting": ["Frequency of vomiting (occasional / frequent / severe):"],
    "diarrhea": ["Severity of diarrhea (mild / moderate / severe):"],
    "runny_nose": ["Runny-nose severity (0-5):"],
    "fatigue": ["Fatigue severity (0-5):"]
}

T3 = {
    ("fever", "rash"): [
        "Did the rash move from face to trunk? (y/n):",
        "Is the tongue 'strawberry' red? (y/n):"
    ],
    ("cough", "fever"): [
        "Is the child having laboured breathing? (y/n):"
    ],
    ("vomiting", "diarrhea"): [
        "Did symptoms start after recent travel? (y/n):"
    ],
    ("fatigue", "runny_nose"): [
        "Was there recent contact with someone sick? (y/n):"
    ]
}

RULE_LEN = {
    "common_cold": 4, "flu": 5, "strep_throat": 4, "ear_infection": 4,
    "bronchitis": 4, "bronchiolitis": 4, "hand_foot_mouth": 3,
    "conjunctivitis": 3, "gastroenteritis": 4, "chickenpox": 4,
    "measles": 5, "mumps": 4, "rubella": 3, "scarlet_fever": 4,
    "roseola": 2, "rsv": 5, "croup": 4, "kawasaki_disease": 4,
    "whooping_cough": 3, "fifth_disease": 3, "food_poisoning": 4,
    "sinusitis": 4  # Added missing diseases from diagnosis.pl
}

DEPT = {
    "common_cold": "General Pediatrics", "flu": "General Pediatrics",
    "strep_throat": "ENT", "ear_infection": "ENT",
    "bronchitis": "Pulmonology", "bronchiolitis": "Pulmonology",
    "hand_foot_mouth": "Dermatology", "conjunctivitis": "Ophthalmology",
    "gastroenteritis": "Gastroenterology", "chickenpox": "Dermatology",
    "measles": "Infectious Disease", "mumps": "Infectious Disease",
    "rubella": "Infectious Disease", "scarlet_fever": "Infectious Disease",
    "roseola": "Pediatrics", "rsv": "Pulmonology", "croup": "Pulmonology",
    "kawasaki_disease": "Cardiology", "whooping_cough": "Pulmonology",
    "fifth_disease": "Dermatology", "food_poisoning": "Gastroenterology",
    "sinusitis": "ENT"  # Added missing departments
}