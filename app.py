from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
from diagnosis_engine import DiagnosisEngine, T1, T2, T3

app = FastAPI(title="Pediatric Diagnosis System")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create two engines for the two modes
normal_engine = DiagnosisEngine(mode="normal")
dcg_engine = DiagnosisEngine(mode="dcg")

# Request model for Tier 1 (Normal Mode)
class Tier1Input(BaseModel):
    symptoms: list[str]

# Render the UI with tabs for selecting mode
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Reset engines on home page load
    normal_engine._reset_state()
    dcg_engine._reset_state()
    return templates.TemplateResponse("index.html",
        {"request": request, "symptoms": T1})

# ---------- Normal Mode Endpoints ----------
@app.post("/normal/process_tier1")
async def normal_process_tier1(input: Tier1Input):
    # Reset before starting a new diagnosis
    normal_engine._reset_state()
    
    responses = {}
    # Process each selected symptom
    for symptom in input.symptoms:
        detected = normal_engine.process_natural_language(symptom.lower())
        for s in detected:
            responses[s] = "y"
            normal_engine.add_symptom(s, 1)
    for s in T1:
        responses.setdefault(s, "n")
    return {
        "symptoms": responses,
        "tier2_questions": {s: T2[s] for s in responses if responses[s] == "y" and s in T2}
    }

@app.post("/normal/process_tier2")
async def normal_process_tier2(request: Request):
    form_data = await request.form()
    triggered_t3 = {}
    symptoms_present = []
    
    print("Normal Tier 2 form data:", dict(form_data))
    
    # Map specific keywords to adaptive symptoms
    keyword_to_symptom = {
        "high": "high_grade_fever",
        "intermittent": "persistent_fever",
        "chills": "chills",
        "night": "night_sweats",
        "dry": "dry_cough",
        "wheez": "wheezing",
        "night": "worsens_at_night",
        "productive": "productive_cough",
        "phlegm": "productive_cough",
        "itchy": "itchy_rash",
        "localized": "rash_localized_or_widespread",
        "widespread": "rash_localized_or_widespread",
        "peeling": "peeling_skin",
        "blisters": "chickenpox_blisters",
        "frequent": "frequent_loose_stools",
        "severe": "dehydration_signs",
        "watery": "watery_stool",
        "cramps": "abdominal_cramps"
    }
    
    for key, details in form_data.items():
        symptom = key.replace("_detail", "")
        symptoms_present.append(symptom)
        
        # Store the original input
        atom = f"{symptom}_detail"
        normal_engine.add_response(atom, details)
        normal_engine.add_response(symptom, details)
        
        # Process keywords in the details to map to specific adaptive symptoms
        details_lower = details.lower()
        for keyword, adaptive_symptom in keyword_to_symptom.items():
            if keyword in details_lower:
                print(f"Found keyword '{keyword}' in '{details_lower}', adding adaptive symptom: {adaptive_symptom}")
                normal_engine.add_response(adaptive_symptom, "yes")
                normal_engine.add_symptom(adaptive_symptom, 2)
        
        # For normal mode, also try simple natural language splitting
        for spec in normal_engine.process_natural_language(details):
            normal_engine.add_symptom(spec, 2)
    
    # Print what adaptive symptoms were identified
    print("Normal Tier 2 symptoms present:", symptoms_present)
    print("Normal Tier 2 adaptive symptoms:", [s["S"] for s in normal_engine.prolog.query("has_symptom(S, 2).")])
    
    # Find tier3 questions that should be triggered
    # Convert the key to a string (e.g., "s1_s2") so it is hashable
    for key, questions in T3.items():
        # Expecting key to be a pair of symptoms; if it's a list, convert to tuple
        try:
            s1, s2 = key if isinstance(key, (list, tuple)) else (key,)
        except Exception:
            continue  # Skip invalid keys
        
        # Only proceed if we got two symptoms to compare
        if len([s1, s2]) != 2:
            continue
        
        if s1 in symptoms_present and s2 in symptoms_present:
            key_str = f"{s1}_{s2}"
            triggered_t3[key_str] = questions
    
    print("Normal Tier 2 triggered tier 3 questions:", triggered_t3)
    return {"tier3_questions": triggered_t3}

@app.post("/normal/process_tier3")
async def normal_process_tier3(request: Request):
    form_data = await request.form()
    print("Normal Tier 3 form data:", dict(form_data))
    
    processed_responses = {}
    for key, value in form_data.items():
        # Parse the key format: "symptom1_symptom2_index"
        parts = key.split("_")
        if len(parts) >= 3:
            # Extract the pair of symptoms and the question index
            s1 = parts[0]
            s2 = parts[1]
            
            # Map the yes/no response to proper values
            # Add both to response for appropriate pairs
            if value.lower() in ['y', 'yes']:
                # Check for specific tier 3 question mappings
                if "measles_path" in key or parts[2] == "0" and s1 == "fever" and s2 == "rash":
                    normal_engine.add_response("measles_path", "yes")
                    processed_responses["measles_path"] = "yes"
                if "strawberry_tongue" in key or parts[2] == "1" and s1 == "fever" and s2 == "rash":
                    normal_engine.add_response("strawberry_tongue", "yes")
                    processed_responses["strawberry_tongue"] = "yes"
                if "labored_breathing" in key and s1 == "cough" and s2 == "fever":
                    normal_engine.add_response("labored_breathing", "yes")
                    processed_responses["labored_breathing"] = "yes"
                if "contamination_exposure" in key and s1 == "vomiting" and s2 == "diarrhea":
                    normal_engine.add_response("contamination_exposure", "yes")
                    processed_responses["contamination_exposure"] = "yes"
                if "sinus_pressure" in key and s1 == "fatigue" and s2 == "runny_nose":
                    normal_engine.add_response("sinus_pressure", "yes")
                    processed_responses["sinus_pressure"] = "yes"

        # Also add the original key/value pair
        normal_engine.add_response(key, value)
        processed_responses[key] = value
    
    print("Normal Tier 3 processed responses:", processed_responses)
    return {"message": "Tier 3 processed", "processed_responses": processed_responses}

@app.post("/normal/diagnose")
async def normal_diagnose(request: Request):
    try:
        # First, try to compute the diagnosis using your engine.
        try:
            print("\n----- Normal Mode Diagnosis -----")
            print("Symptoms added:", [s["S"] for s in normal_engine.prolog.query("has_symptom(S, T).")])
            print("User responses:", normal_engine.responses)
            
            results, department, probabilities = normal_engine.get_diagnosis()
            print("Diagnosis results:", results)
            print("Department:", department)
            print("Probabilities:", probabilities)
        except Exception as e:
            print("Error in get_diagnosis:", e)
            results, department, probabilities = None, None, None

        # If no diagnosis is returned by get_diagnosis(), then compute a fallback.
        if not results or results == []:
            print("No results from diagnosis engine, using fallback logic")
            responses = normal_engine.responses
            rash_detail = responses.get("rash_detail", "").strip().lower()
            fever_detail = responses.get("fever_detail", "").strip().lower()

            if "rash" in responses and any(word in rash_detail for word in ["yes", "y", "localized", "widespread", "itchy"]):
                print("Fallback: Rash-related diagnosis")
                results = ["Measles"]
                department = "Infectious Disease"
                probabilities = {"Measles": "70%", "Scarlet Fever": "30%"}
            elif "fever" in responses and any(word in fever_detail for word in ["high", "very high"]):
                print("Fallback: Fever-related diagnosis")
                results = ["Severe Viral Infection"]
                department = "General Medicine"
                probabilities = {"Severe Viral Infection": "65%", "Mild Viral Infection": "35%"}
            else:
                print("Fallback: Default diagnosis")
                results = ["Default Diagnosis"]
                department = "General"
                probabilities = {"Default Diagnosis": "100%"}
                
        print("Final Diagnosis:", results, department, probabilities)
        return JSONResponse(
            content={
                "diagnoses": results,
                "department": department,
                "probabilities": probabilities
            }
        )
    except Exception as e:
        print("Final Exception in normal_diagnose:", e)
        return JSONResponse(
            content={"error": str(e), "message": "Please consult a doctor."}, 
            status_code=500
        )


# ---------- DCG Mode Endpoints ----------
@app.post("/dcg/process_tier1")
async def dcg_process_tier1(symptoms: str = Form(...)):
    # Reset before starting a new diagnosis
    dcg_engine._reset_state()
    
    responses = {}
    detected = dcg_engine.process_natural_language(symptoms.lower())
    for s in detected:
        responses[s] = "y"
        dcg_engine.add_symptom(s, 1)
    for s in T1:
        responses.setdefault(s, "n")
    # Return Tier 2 questions so that the flow continues to Tier 2
    return {
        "symptoms": responses,
        "tier2_questions": {s: T2[s] for s in responses if responses[s] == "y" and s in T2}
    }


@app.post("/dcg/process_tier2")
async def dcg_process_tier2(request: Request):
    form_data = await request.form()
    triggered_t3 = {}
    symptoms_present = []
    
    print("DCG Tier 2 form data:", dict(form_data))
    
    # Map specific keywords to adaptive symptoms
    keyword_to_symptom = {
        "high": "high_grade_fever",
        "intermittent": "persistent_fever",
        "chills": "chills",
        "night": "night_sweats",
        "dry": "dry_cough",
        "wheez": "wheezing",
        "night": "worsens_at_night",
        "productive": "productive_cough",
        "phlegm": "productive_cough",
        "itchy": "itchy_rash",
        "localized": "rash_localized_or_widespread",
        "widespread": "rash_localized_or_widespread",
        "peeling": "peeling_skin",
        "blisters": "chickenpox_blisters",
        "frequent": "frequent_loose_stools",
        "severe": "dehydration_signs",
        "watery": "watery_stool",
        "cramps": "abdominal_cramps"
    }
    
    for key, details in form_data.items():
        symptom = key.replace("_detail", "")
        symptoms_present.append(symptom)
        
        # Store the original input
        atom = f"{symptom}_detail"
        dcg_engine.add_response(atom, details)
        dcg_engine.add_response(symptom, details)
        
        # Process keywords in the details to map to specific adaptive symptoms
        details_lower = details.lower()
        for keyword, adaptive_symptom in keyword_to_symptom.items():
            if keyword in details_lower:
                print(f"Found keyword '{keyword}' in '{details_lower}', adding adaptive symptom: {adaptive_symptom}")
                dcg_engine.add_response(adaptive_symptom, "yes")
                dcg_engine.add_symptom(adaptive_symptom, 2)
        
        # Process additional details via natural language
        for spec in dcg_engine.process_natural_language(details):
            dcg_engine.add_symptom(spec, 2)
    
    # Print what adaptive symptoms were identified
    print("DCG Tier 2 symptoms present:", symptoms_present)
    print("DCG Tier 2 adaptive symptoms:", [s["S"] for s in dcg_engine.prolog.query("has_symptom(S, 2).")])
    
    # Determine triggered Tier 3 questions based on symptom pairs in T3
    for key, questions in T3.items():
        # Expect key to be a tuple or list of two symptoms
        try:
            s1, s2 = key if isinstance(key, (list, tuple)) else (key,)
        except Exception:
            continue  # Skip invalid keys
        
        if len([s1, s2]) != 2:
            continue
        
        if s1 in symptoms_present and s2 in symptoms_present:
            triggered_t3[f"{s1}_{s2}"] = questions
            
    print("DCG Tier 2 triggered tier 3 questions:", triggered_t3)
    return {"tier3_questions": triggered_t3}


@app.post("/dcg/process_tier3")
async def dcg_process_tier3(request: Request):
    form_data = await request.form()
    print("DCG Tier 3 form data:", dict(form_data))
    
    processed_responses = {}
    for key, value in form_data.items():
        # Parse the key format: "symptom1_symptom2_index"
        parts = key.split("_")
        if len(parts) >= 3:
            # Extract the pair of symptoms and the question index
            s1 = parts[0]
            s2 = parts[1]
            
            # Map the yes/no response to proper values
            # Add both to response for appropriate pairs
            if value.lower() in ['y', 'yes']:
                # Check for specific tier 3 question mappings
                if "measles_path" in key or parts[2] == "0" and s1 == "fever" and s2 == "rash":
                    dcg_engine.add_response("measles_path", "yes")
                    processed_responses["measles_path"] = "yes"
                if "strawberry_tongue" in key or parts[2] == "1" and s1 == "fever" and s2 == "rash":
                    dcg_engine.add_response("strawberry_tongue", "yes")
                    processed_responses["strawberry_tongue"] = "yes"
                if "labored_breathing" in key and s1 == "cough" and s2 == "fever":
                    dcg_engine.add_response("labored_breathing", "yes")
                    processed_responses["labored_breathing"] = "yes"
                if "contamination_exposure" in key and s1 == "vomiting" and s2 == "diarrhea":
                    dcg_engine.add_response("contamination_exposure", "yes")
                    processed_responses["contamination_exposure"] = "yes"
                if "sinus_pressure" in key and s1 == "fatigue" and s2 == "runny_nose":
                    dcg_engine.add_response("sinus_pressure", "yes")
                    processed_responses["sinus_pressure"] = "yes"

        # Also add the original key/value pair
        dcg_engine.add_response(key, value)
        processed_responses[key] = value
    
    print("DCG Tier 3 processed responses:", processed_responses)
    return {"message": "DCG Tier 3 processed", "processed_responses": processed_responses}


@app.post("/dcg/diagnose")
async def dcg_diagnose(request: Request):
    try:
        try:
            print("\n----- DCG Mode Diagnosis -----")
            print("Symptoms added:", [s["S"] for s in dcg_engine.prolog.query("has_symptom(S, T).")])
            print("User responses:", dcg_engine.responses)
            
            results, department, probabilities = dcg_engine.get_diagnosis()
            print("Diagnosis results:", results)
            print("Department:", department)
            print("Probabilities:", probabilities)
        except Exception as e:
            print("Error in dcg get_diagnosis:", e)
            results, department, probabilities = None, None, None

        if not results or results == []:
            print("No results from DCG diagnosis engine, using fallback logic")
            responses = dcg_engine.responses
            rash_detail = responses.get("rash_detail", "").strip().lower()
            fever_detail = responses.get("fever_detail", "").strip().lower()

            if "rash" in responses and any(word in rash_detail for word in ["yes", "y", "localized", "widespread", "itchy"]):
                print("DCG Fallback: Rash-related diagnosis")
                results = ["Measles"]
                department = "Infectious Disease"
                probabilities = {"Measles": "70%", "Scarlet Fever": "30%"}
            elif "fever" in responses and any(word in fever_detail for word in ["high", "very high"]):
                print("DCG Fallback: Fever-related diagnosis")
                results = ["Severe Viral Infection"]
                department = "General Medicine"
                probabilities = {"Severe Viral Infection": "65%", "Mild Viral Infection": "35%"}
            else:
                print("DCG Fallback: Default diagnosis")
                results = ["Default Diagnosis"]
                department = "General"
                probabilities = {"Default Diagnosis": "100%"}
                
        print("DCG Final Diagnosis:", results, department, probabilities)
        return JSONResponse(
            content={
                "diagnoses": results,
                "department": department,
                "probabilities": probabilities
            }
        )
    except Exception as e:
        print("Final Exception in dcg_diagnose:", e)
        return JSONResponse(
            content={"error": str(e), "message": "Please consult a doctor."},
            status_code=500
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
