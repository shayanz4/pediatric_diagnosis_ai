import os
from pyswip import Prolog

# ---------------------------------------------------------------------------
# Initialise Prolog and consult KB files
# ---------------------------------------------------------------------------
prolog = Prolog()
prolog.consult("diagnosis.pl")
prolog.consult("dcg_rules.pl")  # still available if you want Mode 2 later

# Wipe any facts that might be lingering from a previous run (handy in REPL)
prolog.query("retractall(user_response(_, _)).")
prolog.query("retractall(has_symptom(_, _)).")

# ---------------------------------------------------------------------------
# Utility tables – *unchanged*
# ---------------------------------------------------------------------------
rule_lengths = {
    "common_cold": 4, "flu": 5, "strep_throat": 4, "ear_infection": 4,
    "bronchitis": 4, "bronchiolitis": 4, "hand_foot_mouth": 3,
    "conjunctivitis": 3, "gastroenteritis": 4, "chickenpox": 4,
    "measles": 5, "mumps": 4, "rubella": 3, "scarlet_fever": 4,
    "roseola": 2, "rsv": 5, "croup": 4, "kawasaki_disease": 4,
    "whooping_cough": 3, "fifth_disease": 3
}

department_map = {
    "common_cold": "General Pediatrics", "flu": "General Pediatrics",
    "strep_throat": "ENT", "ear_infection": "ENT",
    "bronchitis": "Pulmonology", "bronchiolitis": "Pulmonology",
    "hand_foot_mouth": "Dermatology", "conjunctivitis": "Ophthalmology",
    "gastroenteritis": "Gastroenterology", "chickenpox": "Dermatology",
    "measles": "Infectious Disease", "mumps": "Infectious Disease",
    "rubella": "Infectious Disease", "scarlet_fever": "Infectious Disease",
    "roseola": "Pediatrics", "rsv": "Pulmonology", "croup": "Pulmonology",
    "kawasaki_disease": "Cardiology", "whooping_cough": "Pulmonology",
    "fifth_disease": "Dermatology"
}

# ---------------------------------------------------------------------------
# Tier‑1 screening set‑up (preliminary yes/no)
# ---------------------------------------------------------------------------
tier1_symptoms = [
    "fever", "cough", "rash", "vomiting", "diarrhea", "runny_nose", "fatigue"
]

# ---------------------------------------------------------------------------
# Tier‑2 adaptive questions mapped *directly* to atoms in diagnosis.pl.
# Each entry: (PrologAtom, Prompt)
# ---------------------------------------------------------------------------

tier2_questions = {
    "fever": [
        ("high_grade_fever",      "Is the fever high‑grade (>39 °C)? (y/n)"),
        ("persistent_fever",      "Has the fever lasted more than 3 days? (y/n)"),
        ("chills",                "Is the child experiencing chills? (y/n)"),
        ("night_sweats",          "Are there night sweats? (y/n)")
    ],
    "cough": [
        ("dry_cough",             "Is it a dry cough? (y/n)"),
        ("wheezing",              "Do you hear wheezing? (y/n)"),
        ("worsens_at_night",      "Does the cough worsen at night? (y/n)"),
        ("productive_cough",      "Is the cough productive with sputum? (y/n)")
    ],
    "rash": [
        ("itchy_rash",            "Is the rash itchy? (y/n)"),
        ("rash_localized_or_widespread", "Is the rash widespread (vs local)? (y/n)"),
        ("peeling_skin",          "Is skin peeling? (y/n)")
    ],
    "vomiting": [
        ("blood_in_vomit",        "Is there blood in the vomit? (y/n)"),
        ("dehydration_signs",     "Are there signs of dehydration? (y/n)"),
        ("nausea",                "Is the child nauseous? (y/n)")
    ],
    "diarrhea": [
        ("frequent_loose_stools", "Are stools frequently loose? (y/n)"),
        ("abdominal_cramps",      "Is the child having abdominal cramps? (y/n)"),
        ("watery_stool",          "Is the stool watery? (y/n)")
    ],
    "runny_nose": [
        ("nasal_congestion",      "Is there nasal congestion? (y/n)"),
        ("sneezing",              "Is the child sneezing a lot? (y/n)"),
        ("post_nasal_drip",       "Is there post‑nasal drip? (y/n)")
    ],
    "fatigue": [
        ("chronic_tiredness",     "Is the tiredness persistent or chronic? (y/n)"),
        ("low_energy",            "Is the child low on energy? (y/n)"),
        ("difficulty_concentrating", "Is concentration difficult? (y/n)")
    ]
}

# ---------------------------------------------------------------------------
# Tier‑3 deep‑dive triggers and questions. Same pattern as Tier‑2.
# ---------------------------------------------------------------------------

tier3_triggers = {
    ("fever", "rash"): [
        ("measles_path",        "Did the rash start on the face and spread down? (y/n)"),
        ("strawberry_tongue",   "Is the tongue red and bumpy like a strawberry? (y/n)")
    ],
    ("cough", "fever"): [
        ("labored_breathing",  "Is the child experiencing labored breathing? (y/n)")
    ],
    ("vomiting", "diarrhea"): [
        ("contamination_exposure", "Could this be food or water contamination? (y/n)"),
        ("dehydration_signs",      "Are there signs of dehydration? (y/n)")
    ],
    ("fatigue", "runny_nose"): [
        ("sinus_pressure", "Is there sinus pressure? (y/n)")
    ]
}

# ----------------------------------------------------------------------------
# Helper input functions
# ----------------------------------------------------------------------------

def ask_yes_no(prompt: str) -> str:
    """Return 'yes' or 'no'."""
    while True:
        resp = input(prompt + " ").strip().lower()
        if resp in {"y", "yes"}:
            return "yes"
        if resp in {"n", "no"}:
            return "no"
        print("Please answer y/n.")


def update_progress(done_pct, total_progress=[0]):
    total_progress[0] += done_pct
    pct = min(total_progress[0], 100)
    print(f"✅ You're {pct}% done.")

# ----------------------------------------------------------------------------
# Tier 1 – preliminary yes/no
# ----------------------------------------------------------------------------

def tier1():
    print("\nTier 1 – preliminary screening (y/n)")
    for s in tier1_symptoms:
        ans = ask_yes_no(f"Does the child have {s.replace('_', ' ')}? (y/n):")
        if ans == "yes":
            prolog.assertz(f"has_symptom({s}, 1)")
    update_progress(20)

# ----------------------------------------------------------------------------
# Tier 2 – adaptive questions (for each positive Tier‑1 symptom)
# ----------------------------------------------------------------------------

def tier2():
    print("\nTier 2 – adaptive questions")
    for primary in tier1_symptoms:
        # Only dive deeper if we asserted the primary symptom
        if list(prolog.query(f"has_symptom({primary}, _)")):
            for atom, prompt in tier2_questions.get(primary, []):
                ans = ask_yes_no(prompt)
                prolog.assertz(f"user_response({atom}, {ans})")
    update_progress(40)

# ----------------------------------------------------------------------------
# Tier 3 – deep differentiating questions (trigger pairs)
# ----------------------------------------------------------------------------

def tier3():
    print("\nTier 3 – deep‑dive questions")
    something_asked = False
    for trigger_pair, qlist in tier3_triggers.items():
        if all(list(prolog.query(f"has_symptom({t}, _)")) for t in trigger_pair):
            something_asked = True
            for atom, prompt in qlist:
                ans = ask_yes_no(prompt)
                prolog.assertz(f"user_response({atom}, {ans})")
    if not something_asked:
        print("No deep‑dive questions needed.")
    update_progress(40)

# ----------------------------------------------------------------------------
# Diagnosis summary
# ----------------------------------------------------------------------------

def diagnose():
    print("\nDiagnosis summary:")
    diagnoses = []
    total_weight = 0
    for sol in prolog.query("diagnosis(D)."):
        d = sol["D"]
        if d not in diagnoses:
            diagnoses.append(d)
            total_weight += rule_lengths.get(d, 0)
    if not diagnoses:
        print("No specific diagnosis matched. Please consult a doctor.")
        return

    for d in diagnoses:
        w = rule_lengths.get(d, 0)
        prob = (w / total_weight) * 100 if total_weight else 0
        print(f"- {d.replace('_', ' ').title()} — {prob:.1f}%")

    likely = max(diagnoses, key=lambda x: rule_lengths.get(x, 0))
    dept = department_map.get(likely, "General Pediatrics")
    print(f"\n➡️ Suggested department: {dept}")

# ----------------------------------------------------------------------------
# Main routine – only Mode 1 implemented for now
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Welcome to the Pediatric Diagnosis System (Mode 1 – guided)")
    tier1()
    tier2()
    tier3()
    diagnose()
