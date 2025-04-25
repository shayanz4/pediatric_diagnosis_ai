from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
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
    
    for key, details in form_data.items():
        symptom = key.replace("_detail", "")
        symptoms_present.append(symptom)
        atom = f"{symptom}_detail"
        normal_engine.add_response(atom, details)
        normal_engine.add_response(symptom, details)
        # For normal mode, also try simple natural language splitting
        for spec in normal_engine.process_natural_language(details):
            normal_engine.add_symptom(spec, 2)
    
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
    
    return {"tier3_questions": triggered_t3}

@app.post("/normal/process_tier3")
async def normal_process_tier3(request: Request):
    form_data = await request.form()
    for key, value in form_data.items():
        normal_engine.add_response(key, value)
    return {"message": "Tier 3 processed"}

@app.post("/normal/diagnose")
async def normal_diagnose(request: Request):
    try:
        results, department = normal_engine.get_diagnosis()
        if not results:
            return {"message": "No recognized diagnosis — please consult a doctor."}
        return {"diagnoses": results, "department": department}
    except Exception as e:
        return {"error": str(e), "message": "Please consult a doctor."}

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
    
    for key, details in form_data.items():
        symptom = key.replace("_detail", "")
        symptoms_present.append(symptom)
        atom = f"{symptom}_detail"
        dcg_engine.add_response(atom, details)
        dcg_engine.add_response(symptom, details)
        # Process additional details via natural language
        for spec in dcg_engine.process_natural_language(details):
            dcg_engine.add_symptom(spec, 2)
    
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
            
    return {"tier3_questions": triggered_t3}


@app.post("/dcg/process_tier3")
async def dcg_process_tier3(request: Request):
    form_data = await request.form()
    for key, value in form_data.items():
        dcg_engine.add_response(key, value)
    # Tier 3 processed; now the front-end should allow triggering the final diagnosis.
    return {"message": "DCG Tier 3 processed"}


@app.post("/dcg/diagnose")
async def dcg_diagnose(request: Request):
    try:
        results, department = dcg_engine.get_diagnosis()
        if not results:
            return {"message": "No recognized diagnosis — please consult a doctor."}
        return {"diagnoses": results, "department": department}
    except Exception as e:
        return {"error": str(e), "message": "Please consult a doctor."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)