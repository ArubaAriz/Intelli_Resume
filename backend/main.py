"""
ATS Resume Intelligence Platform — FastAPI Backend
"""

import os
import json
import sqlite3
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import aiofiles

from resume_parser import parse_resume
from nlp_utils import (
    parse_jd_structured,
    get_all_jd_skills,
    predict_career_fit,
    score_projects,
    get_model,
)
from scoring import (
    score_skill_match,
    score_experience_relevance,
    score_resume_quality,
    score_achievements,
    benchmark_candidate,
    generate_recommendations,
    generate_recruiter_view,
    compute_total_score,
)

app = FastAPI(title="ATS Resume Intelligence Platform", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB Setup ──────────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent / "ats.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            created_at TEXT,
            resume_filename TEXT,
            total_score INTEGER,
            result_json TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Pre-warm the embedding model at startup
@app.on_event("startup")
async def startup_event():
    get_model()  # loads once into memory


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0"}


# ── Main Analysis Endpoint ────────────────────────────────────────────────────

@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    """
    Full ATS intelligence analysis.
    Accepts resume (PDF/DOCX) + JD text.
    Returns complete structured analysis.
    """
    # Validate file type
    suffix = Path(resume.filename).suffix.lower()
    if suffix not in (".pdf", ".docx", ".doc"):
        raise HTTPException(400, "Only PDF and DOCX files are supported.")
    
    if len(job_description.strip()) < 50:
        raise HTTPException(400, "Job description is too short. Please paste the full JD.")
    
    # Save temp file
    import tempfile
    import uuid

    tmp_path = tempfile.NamedTemporaryFile(
    delete=False,
    suffix=".pdf"
    ).name
    try:
        async with aiofiles.open(tmp_path, "wb") as f:
            content = await resume.read()
            await f.write(content)
        
        # ── Step 1: Parse Resume ──
        resume_parsed = parse_resume(tmp_path)
        
        # ── Step 2: Parse JD ──
        jd_parsed = parse_jd_structured(job_description)
        jd_skills = get_all_jd_skills(jd_parsed)
        
        resume_skills = resume_parsed.get("skills", [])
        raw_text = resume_parsed.get("raw_text", "")
        
        # ── Step 3: Score Components ──
        skill_result = score_skill_match(resume_skills, jd_parsed)
        
        exp_result = score_experience_relevance(
            resume_parsed.get("experience", []),
            jd_parsed.get("responsibilities", []),
            jd_skills,
        )
        
        project_result = score_projects(
            resume_parsed.get("projects", []),
            jd_skills,
        )
        
        quality_result = score_resume_quality(raw_text)
        
        ach_result = score_achievements(
            resume_parsed.get("achievements", []),
            raw_text,
        )
        
        ats_result = resume_parsed.get("ats_compatibility", {})
        ats_score = ats_result.get("score", 70)
        
        # ── Step 4: Total Score ──
        score_summary = compute_total_score(
            skill_score=skill_result["score"],
            exp_score=exp_result["score"],
            project_score=project_result["score"],
            ats_score=ats_score,
            quality_score=quality_result["score"],
            achievement_score=ach_result["score"],
        )
        
        total = score_summary["total"]
        
        # ── Step 5: Benchmarking ──
        benchmark = benchmark_candidate(
            skill_score=skill_result["score"],
            exp_score=exp_result["score"],
            project_score=project_result["score"],
            ats_score=ats_score,
            quality_score=quality_result["score"],
            total_score=total,
            resume_skills=resume_skills,
        )
        
        # ── Step 6: Career Fit ──
        career_fit = predict_career_fit(resume_skills)
        
        # ── Step 7: Recruiter View ──
        recruiter_view = generate_recruiter_view(
            resume_parsed=resume_parsed,
            jd_parsed=jd_parsed,
            total_score=total,
            skill_score=skill_result,
            quality_score=quality_result,
        )
        
        # ── Step 8: Recommendations ──
        recommendations = generate_recommendations(
            skill_score=skill_result,
            exp_score=exp_result,
            project_score=project_result,
            quality_score=quality_result,
            ats_score=ats_result,
            resume_skills=resume_skills,
            jd_parsed=jd_parsed,
        )
        
        # ── Build Response ──
        result = {
            "id": str(uuid.uuid4()),
            "resume_filename": resume.filename,
            "analyzed_at": datetime.utcnow().isoformat(),
            
            # Parsed data
            "contact": resume_parsed.get("contact", {}),
            "education": resume_parsed.get("education", []),
            "resume_skills": resume_skills,
            "experience": resume_parsed.get("experience", []),
            "projects": resume_parsed.get("projects", []),
            "certifications": resume_parsed.get("certifications", []),
            "achievements": resume_parsed.get("achievements", []),
            
            # JD parsed
            "jd_parsed": jd_parsed,
            
            # Scores
            "total_score": total,
            "score_breakdown": score_summary["breakdown"],
            
            # Individual analyses
            "skill_analysis": skill_result,
            "experience_analysis": exp_result,
            "project_analysis": project_result,
            "quality_analysis": quality_result,
            "achievement_analysis": ach_result,
            "ats_analysis": ats_result,
            
            # Intelligence layers
            "benchmark": benchmark,
            "career_fit": career_fit,
            "recruiter_view": recruiter_view,
            "recommendations": recommendations,
        }
        
        # Persist to SQLite
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO analyses VALUES (?, ?, ?, ?, ?)",
            (result["id"], result["analyzed_at"], resume.filename, total, json.dumps(result)),
        )
        conn.commit()
        conn.close()
        
        return JSONResponse(result)
    
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.get("/history")
def get_history():
    """Get last 20 analyses."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, created_at, resume_filename, total_score FROM analyses ORDER BY created_at DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return [{"id": r[0], "date": r[1], "filename": r[2], "score": r[3]} for r in rows]


@app.get("/history/{analysis_id}")
def get_analysis(analysis_id: str):
    """Retrieve a past analysis."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT result_json FROM analyses WHERE id = ?", (analysis_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Analysis not found")
    return JSONResponse(json.loads(row[0]))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
