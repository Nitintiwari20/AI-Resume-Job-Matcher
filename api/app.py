import json
import os
import joblib
import numpy as np
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.preprocessing import TextPreprocessor
from src.feature_engineering import FeatureEngineer
from src.skill_extractor import SkillExtractor
from src.ats_checker import ATSChecker
from src.recommender import Recommender

app = FastAPI(
    title="AI Resume Job Matcher API",
    version="2.0.0",
    description="Machine Learning based Resume Job Matching & Skill Gap Analysis System"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Instantiate Pipeline Modules
preprocessor = TextPreprocessor()
skill_extractor = SkillExtractor()
ats_service = ATSChecker()
recommender_service = Recommender()

# Load Serialized Trained ML Model & Vectorizer from models/ directory
model_path = os.path.join(MODELS_DIR, "model.pkl")
vectorizer_path = os.path.join(MODELS_DIR, "vectorizer.pkl")

ml_model = None
vectorizer = None

if os.path.exists(model_path) and os.path.exists(vectorizer_path):
    try:
        ml_model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        print("[OK] Successfully loaded model.pkl and vectorizer.pkl into API runtime.")
    except Exception as e:
        print(f"[WARN] Failed loading models: {e}")

feature_engineer = FeatureEngineer(vectorizer)

class MatchRequest(BaseModel):
    resume_text: str
    jd_text: str

class BatchResumeItem(BaseModel):
    id: str
    name: str
    text: str

class BatchMatchRequest(BaseModel):
    jd_text: str
    resumes: List[BatchResumeItem]

class EnhanceBulletRequest(BaseModel):
    bullet: str

def load_json_file(file_name: str):
    path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.get("/api/presets")
def get_presets():
    return {
        "sample_resumes": load_json_file("sample_resumes.json"),
        "sample_jds": load_json_file("sample_jds.json"),
        "skills_db": load_json_file("skills_db.json")
    }

@app.post("/api/parse-resume")
async def parse_resume_endpoint(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None)
):
    if file:
        content = await file.read()
        extracted_text = preprocessor.extract_text_from_file(content, filename=file.filename)
    elif raw_text and raw_text.strip():
        extracted_text = preprocessor.clean_text(raw_text)
    else:
        raise HTTPException(status_code=400, detail="Please upload a file or paste text.")

    contact = preprocessor.extract_contact_info(extracted_text)
    sections = preprocessor.extract_sections(extracted_text)
    skills = skill_extractor.extract_skills(extracted_text)

    parsed_obj = {
        "raw_text": extracted_text,
        "word_count": len(extracted_text.split()),
        "contact": contact,
        "sections": sections
    }
    ats_res = ats_service.analyze(parsed_obj)

    return {
        "parsed": parsed_obj,
        "extracted_skills": skills,
        "ats_analysis": ats_res
    }

@app.post("/api/analyze-match")
def analyze_match_endpoint(req: MatchRequest):
    """
    Core Pipeline Endpoint executing diagram workflow:
    RESUME -> Text Extraction -> Data Cleaning -> Skill Extraction
           -> Resume & Job Features -> Feature Engineering
           -> ML Model -> Match Score -> Strong Skills, Missing Skills, Recommendation
    """
    if not req.resume_text.strip() or not req.jd_text.strip():
        raise HTTPException(status_code=400, detail="Both resume_text and jd_text are required.")

    # 1. Text Cleaning & Normalization
    clean_resume = preprocessor.clean_text(req.resume_text)
    clean_jd = preprocessor.clean_text(req.jd_text)

    # 2. Skill Extraction (Resume & Job Features)
    resume_skills = set(skill_extractor.extract_skills(clean_resume))
    jd_skills = set(skill_extractor.extract_skills(clean_jd))

    matched_skills = sorted(list(resume_skills.intersection(jd_skills)))
    missing_skills = sorted(list(jd_skills - resume_skills))
    extra_skills = sorted(list(resume_skills - jd_skills))

    # 3. Feature Engineering
    features = feature_engineer.extract_features(
        clean_resume, clean_jd, 
        matched_count=len(matched_skills), 
        total_jd_skills=len(jd_skills)
    )

    # 4. ML Model Prediction (.pkl)
    if ml_model is not None:
        predicted_score = float(ml_model.predict(features)[0])
        predicted_score = round(float(np.clip(predicted_score, 0.0, 100.0)), 2)
    else:
        # Fallback weighted score
        skill_score = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 100.0
        tfidf_score = feature_engineer.compute_tfidf_similarity(clean_resume, clean_jd) * 100
        predicted_score = round(0.55 * skill_score + 0.45 * tfidf_score, 2)

    # 5. ATS & Recommendations
    parsed_resume = {
        "raw_text": clean_resume,
        "word_count": len(clean_resume.split()),
        "contact": preprocessor.extract_contact_info(clean_resume),
        "sections": preprocessor.extract_sections(clean_resume)
    }
    ats_analysis = ats_service.analyze(parsed_resume)

    skill_gap = skill_extractor.analyze_skill_gap(clean_resume, clean_jd)
    roadmap = skill_gap["recommendations"]

    # Format skills info for UI
    matched_info = [{"name": s, "category": "Technical"} for s in matched_skills]
    missing_info = [{"name": s, "category": "Required Gap", "resources": {}} for s in missing_skills]

    return {
        "match_analysis": {
            "overall_score": predicted_score,
            "skill_score": round((len(matched_skills) / len(jd_skills) * 100) if jd_skills else 100.0, 2),
            "semantic_score": round(feature_engineer.compute_tfidf_similarity(clean_resume, clean_jd) * 100, 2),
            "skill_gap_matrix": {
                "matched_skills": matched_info,
                "missing_skills": missing_info,
                "extra_skills": extra_skills
            }
        },
        "strong_skills": matched_skills,
        "missing_skills": missing_skills,
        "ats_analysis": ats_analysis,
        "learning_roadmap": roadmap
    }

@app.post("/api/batch-match")
def batch_match_endpoint(req: BatchMatchRequest):
    results = []
    clean_jd = preprocessor.clean_text(req.jd_text)

    for item in req.resumes:
        clean_res = preprocessor.clean_text(item.text)
        res_skills = set(skill_extractor.extract_skills(clean_res))
        jd_skills = set(skill_extractor.extract_skills(clean_jd))

        matched = sorted(list(res_skills.intersection(jd_skills)))
        missing = sorted(list(jd_skills - res_skills))

        feats = feature_engineer.extract_features(clean_res, clean_jd, len(matched), len(jd_skills))
        if ml_model is not None:
            score = round(float(np.clip(ml_model.predict(feats)[0], 0.0, 100.0)), 2)
        else:
            score = round((len(matched)/len(jd_skills)*100 if jd_skills else 100.0), 2)

        parsed = {"raw_text": clean_res, "word_count": len(clean_res.split()), "contact": preprocessor.extract_contact_info(clean_res), "sections": preprocessor.extract_sections(clean_res)}
        ats_res = ats_service.analyze(parsed)

        results.append({
            "id": item.id,
            "name": item.name,
            "overall_score": score,
            "skill_score": round((len(matched)/len(jd_skills)*100 if jd_skills else 100.0), 2),
            "ats_score": ats_res["ats_score"],
            "matched_skills": matched,
            "missing_skills": missing,
            "email": parsed["contact"]["email"]
        })

    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return {"candidate_count": len(results), "leaderboard": results}

@app.post("/api/enhance-bullet")
def enhance_bullet_endpoint(req: EnhanceBulletRequest):
    return recommender_service.enhance_bullet_point(req.bullet)

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Resume Job Matcher API is running."}
