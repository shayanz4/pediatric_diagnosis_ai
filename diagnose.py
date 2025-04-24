import os
from pyswip import Prolog

# Symptom list
symptoms = ["fever", "cough", "fatigue", "runny_nose", "rash"]

# Initialize Prolog
prolog = Prolog()
prolog.consult("diagnosis.pl")

# Ask user for symptom intensities
print("Rate the intensity of each symptom from 1 to 5 (or 0 if not present):")
for symptom in symptoms:
    try:
        intensity = int(input(f"{symptom.capitalize()}: "))
        if intensity > 0:
            prolog.assertz(f"has_symptom({symptom}, {intensity})")
    except ValueError:
        print("Invalid input, skipping...")

# Query diagnosis
print("\nPossible Diagnoses:")
found = False
for result in prolog.query("diagnosis(D)."):
    print(f"- {result['D'].replace('_', ' ').title()}")
    found = True

if not found:
    print("No specific diagnosis matched. Please consult a doctor.")


