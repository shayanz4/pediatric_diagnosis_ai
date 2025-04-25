import os
from pyswip import Prolog

# ── Prolog init ─────────────────────────────────────────────────────
prolog = Prolog()
prolog.consult("dcg_rules.pl")

# ── static config ──────────────────────────────────────────────────
RULE_LEN = {
    "common_cold":4,"flu":5,"strep_throat":4,"ear_infection":4,"bronchitis":4,
    "bronchiolitis":4,"hand_foot_mouth":3,"conjunctivitis":3,"gastroenteritis":4,
    "chickenpox":4,"measles":5,"mumps":4,"rubella":3,"scarlet_fever":4,
    "roseola":2,"rsv":5,"croup":4,"kawasaki_disease":4,"whooping_cough":3,
    "fifth_disease":3
}
DEPT = {
    "common_cold":"General Pediatrics","flu":"General Pediatrics",
    "strep_throat":"ENT","ear_infection":"ENT","bronchitis":"Pulmonology",
    "bronchiolitis":"Pulmonology","hand_foot_mouth":"Dermatology",
    "conjunctivitis":"Ophthalmology","gastroenteritis":"Gastroenterology",
    "chickenpox":"Dermatology","measles":"Infectious Disease",
    "mumps":"Infectious Disease","rubella":"Infectious Disease",
    "scarlet_fever":"Infectious Disease","roseola":"Pediatrics",
    "rsv":"Pulmonology","croup":"Pulmonology","kawasaki_disease":"Cardiology",
    "whooping_cough":"Pulmonology","fifth_disease":"Dermatology"
}

T1 = ["fever","cough","rash","vomiting","diarrhea","runny_nose","fatigue"]

T2 = {
    "fever":[
        "Describe the fever (low-grade / high-grade / intermittent):"
    ],
    "cough":[
        "Type of cough (dry / productive / wheezing):"
    ],
    "rash":[
        "Describe the rash (localized / widespread / itchy):"
    ],
    "vomiting":[
        "Frequency of vomiting (occasional / frequent / severe):"
    ],
    "diarrhea":[
        "Severity of diarrhea (mild / moderate / severe):"
    ],
    "runny_nose":[
        "Runny-nose severity (0-5):"
    ],
    "fatigue":[
        "Fatigue severity (0-5):"
    ]
}

T3 = {
    ("fever","rash"):[
        "Did the rash move from face to trunk? (y/n):",
        "Is the tongue 'strawberry' red? (y/n):"
    ],
    ("cough","fever"):[
        "Is the child having laboured breathing? (y/n):"
    ],
    ("vomiting","diarrhea"):[
        "Did symptoms start after recent travel? (y/n):"
    ],
    ("fatigue","runny_nose"):[
        "Was there recent contact with someone sick? (y/n):"
    ]
}

# ── helpers ─────────────────────────────────────────────────────────
responses = {}
progress = 0

def upd(p):
    global progress 
    progress += p
    print(f"✅ {progress}% complete")

def ask(quest):
    ans = input(quest+" ").strip().lower()
    while not ans: ans = input("Please answer: ").strip().lower()
    return ans

def dcg_parse(text):
    safe = text.replace('"','\"')
    q = f'parse_symptoms("{safe}", S)'
    try:
        r = list(prolog.query(q, maxresult=1))
        return r[0]["S"] if r else []
    except Exception as e:
        print(f"Warning: Error parsing symptoms: {e}")
        return []

# Simplified tier functions for DCG only
def tier1():
    print("\nTier 1 — describe basic symptoms")
    txt = input("Describe symptoms: ").lower()
    for s in dcg_parse(txt):
        responses[s]="y"
        prolog.assertz(f"has_symptom({s},1)")
    for s in T1: responses.setdefault(s,"n")
    upd(20)

def tier2():
    print("\nTier 2 — symptom details")
    for s in responses:
        if responses[s]=="y":
            details = input(f"Describe {s.replace('_',' ')} details: ")
            atom = f"{s}_detail"
            try:
                prolog.assertz(f"user_response({atom},'{details}')")
                prolog.assertz(f"user_response('{s}','{details}')")  # Add direct severity
                # Also assert any specific symptoms mentioned in details
                specific_symptoms = dcg_parse(details)
                for spec in specific_symptoms:
                    prolog.assertz(f"has_symptom({spec},2)")
            except Exception as e:
                print(f"Warning: Could not process detail: {e}")
    upd(40)

def tier3():
    print("\nTier 3 — additional information")
    triggered = False
    for trig,qs in T3.items():
        if all(responses.get(t)=="y" for t in trig):
            triggered = True
            for q in qs:
                details = input(q+" ")
                atom = f"{trig[0]}_{trig[1]}_detail"
                prolog.assertz(f"user_response({atom},'{details}')")
    if not triggered: print("No additional questions needed.")
    upd(40)

# ── diagnosis ──────────────────────────────────────────────────────
def diagnose():
    print("\nDiagnosis")
    try:
        dx = [d["Disease"] for d in prolog.query("diagnosis(Disease).")]
        dx = list(dict.fromkeys(dx))        # preserve order, unique
        if not dx:
            print("No match — please consult a doctor.")
            return
        
        # Filter only known diseases
        dx = [d for d in dx if d in RULE_LEN]
        
        if not dx:
            print("No recognized diagnosis — please consult a doctor.")
            return
            
        total = sum(RULE_LEN.get(d,1) for d in dx)
        for d in dx:
            p = RULE_LEN.get(d,1)*100/total
            print(f"- {d.replace('_',' ').title():20}  {p:5.1f}%")
        best = max(dx, key=lambda d: RULE_LEN.get(d,0))
        print(f"\nSuggested department: {DEPT.get(best,'General Pediatrics')}")
    except Exception as e:
        print(f"Error during diagnosis: {e}")
        print("Please consult a doctor.")

# ── main ───────────────────────────────────────────────────────────
if __name__=="__main__":
    print("Pediatric Diagnosis System (Natural Language Mode)\n")
    tier1()
    tier2()
    tier3()
    diagnose()