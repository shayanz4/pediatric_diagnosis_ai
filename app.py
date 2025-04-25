from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from diagnosis_engine import DiagnosisEngine, T1, T2, T3

app = FastAPI(title="Pediatric Diagnosis System")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create two engines for the two modes
normal_engine = DiagnosisEngine(mode="normal")
dcg_engine = DiagnosisEngine(mode="dcg")

# Render the UI with tabs for selecting mode
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html",
        {"request": request, "tier1_symptoms": T1})

# ---------- Normal Mode Endpoints ----------
@app.post("/normal/process_tier1")
async def normal_process_tier1(symptoms: str = Form(...)):
    responses = {}
    detected = normal_engine.process_natural_language(symptoms.lower())
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
    for s, details in form_data.items():
        atom = f"{s}_detail"
        normal_engine.add_response(atom, details)
        normal_engine.add_response(s, details)
        # For normal mode, also try simple natural language splitting
        for spec in normal_engine.process_natural_language(details):
            normal_engine.add_symptom(spec, 2)
    symptoms_present = [s.replace("_detail", "") for s in form_data.keys()]
    for (s1, s2), questions in T3.items():
        if s1 in symptoms_present and s2 in symptoms_present:
            triggered_t3[(s1, s2)] = questions
    return {"tier3_questions": triggered_t3}

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
    responses = {}
    detected = dcg_engine.process_natural_language(symptoms.lower())
    for s in detected:
        responses[s] = "y"
        dcg_engine.add_symptom(s, 1)
    for s in T1:
        responses.setdefault(s, "n")
    return {
        "symptoms": responses,
        "tier2_questions": {s: T2[s] for s in responses if responses[s] == "y" and s in T2}
    }

@app.post("/dcg/process_tier2")
async def dcg_process_tier2(request: Request):
    form_data = await request.form()
    triggered_t3 = {}
    for s, details in form_data.items():
        atom = f"{s}_detail"
        dcg_engine.add_response(atom, details)
        dcg_engine.add_response(s, details)
        for spec in dcg_engine.process_natural_language(details):
            dcg_engine.add_symptom(spec, 2)
    symptoms_present = [s.replace("_detail", "") for s in form_data.keys()]
    for (s1, s2), questions in T3.items():
        if s1 in symptoms_present and s2 in symptoms_present:
            triggered_t3[(s1, s2)] = questions
    return {"tier3_questions": triggered_t3}

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