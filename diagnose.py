import os
from pyswip import Prolog

# Initialize Prolog
prolog = Prolog()
prolog.consult("diagnosis.pl")

# Rule lengths for probability calculation
rule_lengths = {
    "common_cold": 4,
    "flu": 5,
    "strep_throat": 4,
    "ear_infection": 4,
    "bronchitis": 4,
    "bronchiolitis": 4,
    "hand_foot_mouth": 3,
    "conjunctivitis": 3,
    "gastroenteritis": 4,
    "chickenpox": 4,
    "measles": 5,
    "mumps": 4,
    "rubella": 3,
    "scarlet_fever": 4,
    "roseola": 2,
    "rsv": 5,
    "croup": 4,
    "kawasaki_disease": 4,
    "whooping_cough": 3,
    "fifth_disease": 3
}

# Department suggestions
department_map = {
    "common_cold": "General Pediatrics",
    "flu": "General Pediatrics",
    "strep_throat": "ENT",
    "ear_infection": "ENT",
    "bronchitis": "Pulmonology",
    "bronchiolitis": "Pulmonology",
    "hand_foot_mouth": "Dermatology",
    "conjunctivitis": "Ophthalmology",
    "gastroenteritis": "Gastroenterology",
    "chickenpox": "Dermatology",
    "measles": "Infectious Disease",
    "mumps": "Infectious Disease",
    "rubella": "Infectious Disease",
    "scarlet_fever": "Infectious Disease",
    "roseola": "Pediatrics",
    "rsv": "Pulmonology",
    "croup": "Pulmonology",
    "kawasaki_disease": "Cardiology",
    "whooping_cough": "Pulmonology",
    "fifth_disease": "Dermatology"
}

# Tiered symptom groups
tier1_symptoms = ["fever", "cough", "runny_nose", "rash", "vomiting", "diarrhea", "fatigue"]
tier2_questions = {
    "fever": ["On a scale of 0-5, how severe is the fever?",
              "Describe the fever (e.g., high-grade, intermittent, low-grade):"],
    "cough": ["Describe the type of cough (e.g., dry, productive, wheezing):",
              "When is the cough most severe (e.g., morning, night, all day)?: "],
    "rash": ["Describe the rash (e.g., localized, widespread, itchy, red spots):"],
    "vomiting": ["How frequent is the vomiting (e.g., occasional, frequent, severe)?: ",
                 "Describe any noticeable characteristics of the vomit (e.g., with blood, clear):"],
    "diarrhea": ["How severe is the diarrhea (e.g., mild, moderate, severe)?: ",
                 "Describe any noticeable changes in the stool (e.g., with blood, watery):"],
    "runny_nose": ["On a scale of 0-5, how severe is the runny nose?: "],
    "fatigue": ["On a scale of 0-5, how severe is the fatigue?: ",
                "Describe the fatigue (e.g., constant, intermittent, worsens during the day):"]
}
tier3_triggers = {
    ("fever", "rash"): ["Did the rash spread from the face to the trunk? (y/n): ",
                        "Is the tongue red and bumpy like a 'strawberry'? (y/n): "],
    ("cough", "fever"): ["Is the child experiencing labored breathing? (y/n): "],
    ("vomiting", "fatigue"): ["Did these symptoms begin after recent travel? (y/n): "]
}

# Store user responses
user_responses = {}
progress = 0

def sanitize_for_prolog(text):
    return (
        text.replace(" ", "_")  # Replace spaces with underscores
        .replace("?", "")       # Remove question marks
        .replace("/", "_or_")   # Replace slashes with "_or_"
        .replace("'", "_")      # Replace single quotes with underscores
        .replace("°", "deg")    # Replace degree symbols with "deg"
        .replace(",", "")       # Remove commas
        .replace(".", "")       # Remove periods
        .replace("(", "")       # Remove parentheses
        .replace(")", "")       # Remove parentheses
        .replace("-", "_")      # Replace dash with underscore (Prolog-safe)
        .replace(":", "")       # Remove colons (Prolog-safe)
    )

def ask_typed_response(question):
    while True:
        response = input(f"{question}: ").strip().lower()
        if response:
            return response
        print("Please provide a valid response.")

def ask_intensity(question):
    while True:
        try:
            response = int(input(f"{question} (0-5): "))
            if 0 <= response <= 5:
                return response
            else:
                print("Please enter a number between 0 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number between 0 and 5.")

def update_progress(amount):
    global progress
    progress += amount
    if progress >= 100:
        print("✅ You're done!")
    else:
        print(f"✅ You're {progress}% done.")

def check_conflict(symptom, new_response):
    existing_response = user_responses.get(symptom)
    if existing_response and existing_response != new_response:
        print(f"Warning: Conflicting response detected for '{symptom}'. Previous: {existing_response}, New: {new_response}.")
        return True
    return False

# Tier 1: Preliminary Screening
def tier1_screening():
    print("\nTier 1: Preliminary Screening")
    for symptom in tier1_symptoms:
        response = ask_typed_response(f"Do they have {symptom.replace('_', ' ')}? (y/n)")
        if check_conflict(symptom, response):
            continue
        user_responses[symptom] = response
        if response == "y":
            prolog.assertz(f"has_symptom({symptom}, 1)")
    update_progress(15)

def tier2_questioning():
    print("\nTier 2: Adaptive Questioning")
    for symptom, questions in tier2_questions.items():
        if user_responses.get(symptom) == "y":  # Adjusted for y/n responses
            for question in questions:
                response = ask_typed_response(question)
                sanitized_question = sanitize_for_prolog(question)
                if check_conflict(sanitized_question, response):
                    continue
                user_responses[question] = response
                prolog.assertz(f"user_response({sanitized_question}, '{response}')")
    update_progress(35)

# Tier 3: Deep Adaptive Questioning
def tier3_questioning():
    print("\nTier 3: Deep Adaptive Questioning")
    deep_adaptive_done = False
    for trigger, questions in tier3_triggers.items():
        if all(user_responses.get(symptom) == "y" for symptom in trigger):
            deep_adaptive_done = True
            for question in questions:
                response = ask_typed_response(question)
                sanitized_question = sanitize_for_prolog(question)
                if check_conflict(sanitized_question, response):
                    continue
                user_responses[question] = response
                prolog.assertz(f"user_response({sanitized_question}, '{response}')")
    if not deep_adaptive_done:
        print("No deep adaptive questioning needed.")
    update_progress(50)

# Diagnosis and Recommendation
def diagnose():
    print("\nDiagnosis Summary")
    diagnoses = []
    total_weight = 0
    for result in prolog.query("diagnosis(Disease)."):
        disease = result["Disease"]
        if disease not in diagnoses:
            diagnoses.append(disease)
            total_weight += rule_lengths.get(disease, 0)
    if diagnoses:
        for disease in diagnoses:
            weight = rule_lengths.get(disease, 0)
            prob = (weight / total_weight) * 100 if total_weight > 0 else 0
            print(f"- {disease.replace('_', ' ').title()} — {prob:.2f}% probability")
        most_probable = max(diagnoses, key=lambda d: rule_lengths.get(d, 0))
        department = department_map.get(most_probable, "General Pediatrics")
        print(f"\nBased on your symptoms, we recommend consulting the {department} department. We hope you are satisfied with our services!")
    else:
        print("No specific diagnosis matched. Please consult a healthcare provider.")

# Main workflow
if __name__ == "__main__":
    tier1_screening()
    tier2_questioning()
    tier3_questioning()
    diagnose()






