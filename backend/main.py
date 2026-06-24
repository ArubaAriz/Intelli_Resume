
"""
ATS Resume Intelligence Platform — FastAPI Backend
"""

import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

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

app = FastAPI(
    title="ATS Resume Intelligence Platform",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "2.0"
    }


# ─────────────────────────────────────────────────────────────
# Main ATS Analysis Endpoint
# ─────────────────────────────────────────────────────────────

@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Full ATS Resume Intelligence Analysis
    """

    suffix = Path(resume.filename).suffix.lower()

    if suffix not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    if len(job_description.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short."
        )

    tmp_path = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ).name

    try:

        async with aiofiles.open(tmp_path, "wb") as f:
            content = await resume.read()
            await f.write(content)

        # Resume Parsing
        resume_parsed = parse_resume(tmp_path)

        # JD Parsing
        jd_parsed = parse_jd_structured(job_description)

        jd_skills = get_all_jd_skills(jd_parsed)

        resume_skills = resume_parsed.get("skills", [])
        raw_text = resume_parsed.get("raw_text", "")

        # Skill Match
        skill_result = score_skill_match(
            resume_skills,
            jd_parsed
        )

        # Experience Relevance
        exp_result = score_experience_relevance(
            resume_parsed.get("experience", []),
            jd_parsed.get("responsibilities", []),
            jd_skills
        )

        # Project Relevance
        project_result = score_projects(
            resume_parsed.get("projects", []),
            jd_skills
        )

        # Resume Quality
        quality_result = score_resume_quality(raw_text)

        # Achievements
        ach_result = score_achievements(
            resume_parsed.get("achievements", []),
            raw_text
        )

        ats_result = resume_parsed.get(
            "ats_compatibility",
            {}
        )

        ats_score = ats_result.get("score", 70)

        # Total Score
        score_summary = compute_total_score(
            skill_score=skill_result["score"],
            exp_score=exp_result["score"],
            project_score=project_result["score"],
            ats_score=ats_score,
            quality_score=quality_result["score"],
            achievement_score=ach_result["score"]
        )

        total_score = score_summary["total"]

        # Benchmarking
        benchmark = benchmark_candidate(
            skill_score=skill_result["score"],
            exp_score=exp_result["score"],
            project_score=project_result["score"],
            ats_score=ats_score,
            quality_score=quality_result["score"],
            total_score=total_score,
            resume_skills=resume_skills
        )

        # Career Fit
        career_fit = predict_career_fit(
            resume_skills
        )

        # Recruiter View
        recruiter_view = generate_recruiter_view(
            resume_parsed=resume_parsed,
            jd_parsed=jd_parsed,
            total_score=total_score,
            skill_score=skill_result,
            quality_score=quality_result
        )

        # Recommendations
        recommendations = generate_recommendations(
            skill_score=skill_result,
            exp_score=exp_result,
            project_score=project_result,
            quality_score=quality_result,
            ats_score=ats_result,
            resume_skills=resume_skills,
            jd_parsed=jd_parsed
        )

        result = {
            "id": str(uuid.uuid4()),
            "resume_filename": resume.filename,
            "analyzed_at": datetime.utcnow().isoformat(),

            "contact": resume_parsed.get("contact", {}),
            "education": resume_parsed.get("education", []),
            "resume_skills": resume_skills,
            "experience": resume_parsed.get("experience", []),
            "projects": resume_parsed.get("projects", []),
            "certifications": resume_parsed.get("certifications", []),
            "achievements": resume_parsed.get("achievements", []),

            "jd_parsed": jd_parsed,

            "total_score": total_score,
            "score_breakdown": score_summary["breakdown"],

            "skill_analysis": skill_result,
            "experience_analysis": exp_result,
            "project_analysis": project_result,
            "quality_analysis": quality_result,
            "achievement_analysis": ach_result,
            "ats_analysis": ats_result,

            "benchmark": benchmark,
            "career_fit": career_fit,
            "recruiter_view": recruiter_view,
            "recommendations": recommendations
        }

        return JSONResponse(content=result)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )

