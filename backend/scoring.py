"""
Scoring engine for ATS Resume Intelligence Platform.
Weights: Skill Match 35% | Experience 25% | Projects 15% | ATS 10% | Quality 10% | Achievements 5%
"""

import re
from typing import Dict, List, Tuple

from nlp_utils import (
    find_semantic_matches,
    semantic_similarity,
    analyze_action_verbs,
    detect_quantified_achievements,
    score_projects,
    predict_career_fit,
    get_all_jd_skills,
    STRONG_VERBS,
    WEAK_VERBS,
)


def score_skill_match(
    resume_skills: List[str],
    jd_parsed: Dict,
) -> Dict:
    """
    Skill match using semantic similarity. 35% weight.
    """
    jd_skills = get_all_jd_skills(jd_parsed)
    if not jd_skills:
        return {"score": 50, "matched": [], "missing": [], "jd_skills": []}
    
    matched, missing = find_semantic_matches(jd_skills, resume_skills, threshold=0.55)
    
    # Score = matched / total JD skills
    raw_score = len(matched) / len(jd_skills) * 100
    
    # Also factor in semantic quality of matches
    if matched:
        avg_match_quality = sum(m["score"] for m in matched) / len(matched)
        raw_score = raw_score * (0.7 + 0.3 * avg_match_quality)
    
    return {
        "score": round(min(raw_score, 100)),
        "matched": matched,
        "missing": missing,
        "jd_skills": jd_skills,
        "soft_skills_match": _check_soft_skills(
            resume_skills, jd_parsed.get("soft_skills", [])
        ),
    }


def _check_soft_skills(resume_skills: List[str], jd_soft: List[str]) -> Dict:
    if not jd_soft:
        return {"matched": [], "missing": []}
    matched = [s for s in jd_soft if s in resume_skills]
    missing = [s for s in jd_soft if s not in resume_skills]
    return {"matched": matched, "missing": missing}


def score_experience_relevance(
    experience: List[Dict],
    jd_responsibilities: List[str],
    jd_skills: List[str],
) -> Dict:
    """
    Experience relevance vs JD responsibilities. 25% weight.
    Uses semantic similarity.
    """
    if not experience:
        return {"score": 0, "explanation": "No work experience detected.", "details": []}
    
    # Build corpus of resume experience text
    exp_texts = []
    for exp in experience:
        exp_texts.append(f"{exp.get('role', '')} {exp.get('description', '')}")
    
    combined_exp = " ".join(exp_texts)
    
    # Score against JD responsibilities
    resp_score = 0.0
    if jd_responsibilities:
        resp_score = semantic_similarity(jd_responsibilities, exp_texts)
    
    # Score skills used in experience vs JD
    exp_skills = []
    for exp in experience:
        exp_skills.extend(exp.get("skills_used", []))
    exp_skills = list(set(exp_skills))
    
    skill_overlap = len(set(exp_skills) & set(jd_skills)) / max(len(jd_skills), 1) if jd_skills else 0
    
    # Combined score
    if jd_responsibilities:
        raw_score = (resp_score * 0.6 + skill_overlap * 0.4) * 100
    else:
        raw_score = skill_overlap * 100
    
    # Experience depth bonus
    total_entries = len(experience)
    if total_entries >= 3:
        raw_score = min(raw_score * 1.1, 100)
    
    # Explanation
    matched_skill_count = len(set(exp_skills) & set(jd_skills))
    explanation = (
        f"Your experience demonstrates {matched_skill_count} of {len(jd_skills)} required skills. "
    )
    if resp_score > 0.6:
        explanation += "Your responsibilities align well with the job requirements."
    elif resp_score > 0.4:
        explanation += "Some responsibilities match, but deeper alignment in key areas would strengthen your application."
    else:
        explanation += "Consider highlighting experience that maps more directly to the listed responsibilities."
    
    return {
        "score": round(min(raw_score, 100)),
        "explanation": explanation,
        "details": [
            {"label": "Responsibility Alignment", "score": round(resp_score * 100)},
            {"label": "Skills in Experience", "score": round(skill_overlap * 100)},
        ],
    }


def score_resume_quality(text: str) -> Dict:
    """Resume writing quality analysis. 10% weight."""
    verb_analysis = analyze_action_verbs(text)
    achievement_analysis = detect_quantified_achievements(text)
    
    # Score components
    verb_score = min(
        (verb_analysis["strong_count"] * 10 - verb_analysis["weak_count"] * 5), 100
    )
    verb_score = max(verb_score, 0)
    
    quant_score = achievement_analysis["quantification_rate"] * 100
    
    # Length adequacy
    word_count = len(text.split())
    if 300 <= word_count <= 900:
        length_score = 100
    elif word_count < 300:
        length_score = (word_count / 300) * 100
    else:
        length_score = max(100 - (word_count - 900) / 10, 60)
    
    overall = (verb_score * 0.4 + quant_score * 0.4 + length_score * 0.2)
    
    return {
        "score": round(min(overall, 100)),
        "strong_verbs": verb_analysis["strong_verbs"][:8],
        "weak_verbs": verb_analysis["weak_verbs"][:5],
        "quantified_achievements": achievement_analysis["quantified"][:4],
        "unquantified_examples": achievement_analysis["unquantified"][:3],
        "word_count": word_count,
        "components": {
            "action_verbs": round(verb_score),
            "quantification": round(quant_score),
            "length": round(length_score),
        },
    }


def score_achievements(achievements: List[str], text: str) -> Dict:
    """Achievement quality score. 5% weight."""
    if not achievements:
        # Look in raw text
        ach_patterns = [
            r'(?:award|honor|recognition|prize|rank|finalist|winner)',
            r'(?:dean\'s list|scholarship|fellowship)',
            r'top \d+%',
            r'\d+\s*(?:publications?|papers?|patents?)',
        ]
        found = sum(1 for p in ach_patterns if re.search(p, text, re.I))
        score = min(found * 25, 100)
        return {"score": score, "items": [], "from_text": True}
    
    score = min(len(achievements) * 20, 100)
    return {"score": score, "items": achievements[:5]}


def benchmark_candidate(
    skill_score: float,
    exp_score: float,
    project_score: float,
    ats_score: float,
    quality_score: float,
    total_score: float,
    resume_skills: List[str],
) -> Dict:
    """
    Compare candidate against market benchmarks.
    Estimates percentile, interview probability, hiring readiness.
    """
    # Simple percentile model based on total score
    if total_score >= 82:
        percentile = "Top 10%"
        interview_prob = "85-95%"
        readiness = "Highly Ready"
        color = "green"
    elif total_score >= 70:
        percentile = "Top 25%"
        interview_prob = "65-80%"
        readiness = "Ready"
        color = "blue"
    elif total_score >= 55:
        percentile = "Top 50%"
        interview_prob = "35-55%"
        readiness = "Needs Improvement"
        color = "yellow"
    elif total_score >= 40:
        percentile = "Top 65%"
        interview_prob = "15-30%"
        readiness = "Weak Match"
        color = "orange"
    else:
        percentile = "Bottom 50%"
        interview_prob = "< 15%"
        readiness = "Not Ready"
        color = "red"
    
    # Skills breadth score
    skill_breadth = min(len(resume_skills) * 4, 100)
    
    radar_data = [
        {"metric": "Technical Skills", "score": round(skill_score)},
        {"metric": "Experience", "score": round(exp_score)},
        {"metric": "Projects", "score": round(project_score)},
        {"metric": "Resume Quality", "score": round(quality_score)},
        {"metric": "ATS Readiness", "score": round(ats_score)},
        {"metric": "Skill Breadth", "score": round(skill_breadth)},
    ]
    
    return {
        "percentile": percentile,
        "interview_probability": interview_prob,
        "hiring_readiness": readiness,
        "readiness_color": color,
        "radar_data": radar_data,
        "total_score": round(total_score),
    }


def generate_recommendations(
    skill_score: Dict,
    exp_score: Dict,
    project_score: Dict,
    quality_score: Dict,
    ats_score: Dict,
    resume_skills: List[str],
    jd_parsed: Dict,
) -> List[Dict]:
    """Generate specific, actionable recommendations. Never generic advice."""
    recs = []
    
    # Skill gaps → specific missing skills
    missing = skill_score.get("missing", [])
    if missing:
        top_missing = missing[:3]
        skills_str = ", ".join(top_missing)
        recs.append({
            "priority": "high",
            "category": "Skill Gap",
            "title": f"Add {top_missing[0].title()} to your skill set",
            "detail": (
                f"The JD requires {skills_str}. These are not clearly demonstrated in your resume. "
                f"Consider adding projects or certifications that showcase {top_missing[0]}."
            ),
        })
    
    # Cloud skills missing
    cloud_skills = jd_parsed.get("cloud", [])
    resume_lower = [s.lower() for s in resume_skills]
    missing_cloud = [c for c in cloud_skills if c not in resume_lower]
    if missing_cloud:
        recs.append({
            "priority": "high",
            "category": "Cloud Skills",
            "title": f"Add {missing_cloud[0].upper()} experience",
            "detail": (
                f"This role requires {', '.join(missing_cloud)} expertise. "
                f"Consider deploying a side project to {missing_cloud[0].upper()} or earning a free-tier certification."
            ),
        })
    
    # Weak verbs
    weak = quality_score.get("weak_verbs", [])
    if weak:
        recs.append({
            "priority": "medium",
            "category": "Resume Writing",
            "title": "Replace weak action verbs with impact-driven language",
            "detail": (
                f"Phrases like '{weak[0]}' undermine your experience. "
                "Replace with: Developed, Engineered, Optimized, Architected, or Delivered."
            ),
        })
    
    # Quantification
    unquantified = quality_score.get("unquantified_examples", [])
    if unquantified:
        recs.append({
            "priority": "medium",
            "category": "Impact Metrics",
            "title": "Quantify your project and work achievements",
            "detail": (
                "Add metrics to your bullets. Example: instead of 'Built a chatbot', write "
                "'Built an AI chatbot that reduced customer response time by 40% for 10,000 monthly users.'"
            ),
        })
    
    # ATS issues
    ats_issues = ats_score.get("issues", [])
    errors = [i for i in ats_issues if i["type"] == "error"]
    if errors:
        recs.append({
            "priority": "high",
            "category": "ATS Formatting",
            "title": errors[0]["msg"],
            "detail": "Fix this immediately — ATS systems may reject your resume before a human sees it.",
        })
    
    # Low experience relevance
    if exp_score.get("score", 0) < 50:
        recs.append({
            "priority": "medium",
            "category": "Experience Alignment",
            "title": "Reframe work experience to match JD responsibilities",
            "detail": (
                "Tailor your bullet points to mirror the language in the job description. "
                "If the JD says 'deploy ML models to production', and you have done this, say so explicitly."
            ),
        })
    
    # Project suggestions
    if project_score.get("score", 0) < 40:
        domain = jd_parsed.get("domain", [""])
        domain_str = domain[0] if domain else "this domain"
        recs.append({
            "priority": "medium",
            "category": "Projects",
            "title": f"Add a production-level project aligned with {domain_str}",
            "detail": (
                "Recruiters value real-world impact. Build and deploy a project using the exact "
                "tech stack in the JD — even a small end-to-end project shows capability better than listing skills."
            ),
        })
    
    # LinkedIn / GitHub
    recs.append({
        "priority": "low",
        "category": "Professional Presence",
        "title": "Ensure LinkedIn and GitHub are linked and active",
        "detail": "70% of recruiters check LinkedIn. Pin your best repositories and ensure your GitHub shows recent activity.",
    })
    
    return recs[:8]


def generate_recruiter_view(
    resume_parsed: Dict,
    jd_parsed: Dict,
    total_score: float,
    skill_score: Dict,
    quality_score: Dict,
) -> Dict:
    """What would a recruiter notice about this resume?"""
    strengths = []
    weaknesses = []
    
    # Strengths
    if skill_score.get("score", 0) > 65:
        strengths.append("Strong technical skill alignment with the JD requirements")
    if quality_score.get("strong_verbs"):
        strengths.append(f"Uses strong action verbs: {', '.join(quality_score['strong_verbs'][:3])}")
    if resume_parsed.get("projects"):
        strengths.append(f"{len(resume_parsed['projects'])} projects showcase hands-on experience")
    if resume_parsed.get("certifications"):
        strengths.append(f"Has {len(resume_parsed['certifications'])} relevant certifications")
    if quality_score.get("quantified_achievements"):
        strengths.append("Includes quantified achievements — recruiters notice this immediately")
    if resume_parsed.get("contact", {}).get("github"):
        strengths.append("GitHub profile provided — demonstrates open-source/portfolio presence")
    
    # Weaknesses
    if skill_score.get("score", 0) < 50:
        missing = skill_score.get("missing", [])[:3]
        if missing:
            weaknesses.append(f"Missing key skills: {', '.join(missing)}")
    if quality_score.get("weak_verbs"):
        weaknesses.append(f"Weak action verbs ({', '.join(quality_score['weak_verbs'][:2])}) reduce perceived impact")
    if not quality_score.get("quantified_achievements"):
        weaknesses.append("No quantified achievements — makes it hard to assess impact")
    ats_issues = resume_parsed.get("ats_compatibility", {}).get("issues", [])
    errors = [i for i in ats_issues if i["type"] == "error"]
    if errors:
        weaknesses.append(f"ATS issue: {errors[0]['msg']}")
    if not resume_parsed.get("contact", {}).get("linkedin"):
        weaknesses.append("No LinkedIn URL — reduces profile discoverability")
    
    # First impression (recruiter's 6-second scan)
    if total_score >= 75:
        first_impression = "Strong candidate — likely to advance to phone screening"
    elif total_score >= 55:
        first_impression = "Moderate fit — may advance if JD flexibility exists"
    else:
        first_impression = "Weak match — unlikely to proceed without significant changes"
    
    return {
        "strengths": strengths[:5],
        "weaknesses": weaknesses[:5],
        "first_impression": first_impression,
        "interview_readiness": "High" if total_score >= 75 else "Medium" if total_score >= 55 else "Low",
        "hiring_readiness": "Strong" if total_score >= 80 else "Moderate" if total_score >= 60 else "Weak",
    }


def compute_total_score(
    skill_score: float,
    exp_score: float,
    project_score: float,
    ats_score: float,
    quality_score: float,
    achievement_score: float,
) -> Dict:
    """Weighted total score breakdown."""
    weights = {
        "skill_match": 0.35,
        "experience_relevance": 0.25,
        "project_relevance": 0.15,
        "ats_compatibility": 0.10,
        "resume_quality": 0.10,
        "achievements": 0.05,
    }
    
    scores = {
        "skill_match": skill_score,
        "experience_relevance": exp_score,
        "project_relevance": project_score,
        "ats_compatibility": ats_score,
        "resume_quality": quality_score,
        "achievements": achievement_score,
    }
    
    total = sum(scores[k] * weights[k] for k in weights)
    
    breakdown = [
        {
            "category": "Skill Match",
            "weight": "35%",
            "score": round(skill_score),
            "weighted": round(skill_score * 0.35, 1),
        },
        {
            "category": "Experience Relevance",
            "weight": "25%",
            "score": round(exp_score),
            "weighted": round(exp_score * 0.25, 1),
        },
        {
            "category": "Project Relevance",
            "weight": "15%",
            "score": round(project_score),
            "weighted": round(project_score * 0.15, 1),
        },
        {
            "category": "ATS Compatibility",
            "weight": "10%",
            "score": round(ats_score),
            "weighted": round(ats_score * 0.10, 1),
        },
        {
            "category": "Resume Quality",
            "weight": "10%",
            "score": round(quality_score),
            "weighted": round(quality_score * 0.10, 1),
        },
        {
            "category": "Achievements",
            "weight": "5%",
            "score": round(achievement_score),
            "weighted": round(achievement_score * 0.05, 1),
        },
    ]
    
    return {"total": round(total), "breakdown": breakdown}
