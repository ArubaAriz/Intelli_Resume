"""
NLP utilities for ATS Resume Intelligence Platform.
Handles skill extraction, semantic similarity, and structured parsing.
"""

import re
import math
import json
from typing import List, Dict, Tuple, Optional
from collections import Counter

# ── Optional sentence-transformers ───────────────────────────────────────────
_model = None
_model_loaded = False

def get_model():
    global _model, _model_loaded
    if _model_loaded:
        return _model
    _model_loaded = True
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[NLP] sentence-transformers model loaded")
    except Exception as e:
        print(f"[NLP] sentence-transformers unavailable ({e}), using TF-IDF fallback")
        _model = None
    return _model


# ── TF-IDF fallback similarity ────────────────────────────────────────────────
def _tokenize(text: str) -> List[str]:
    return re.findall(r'\b[a-z][a-z0-9\+\#\.]*\b', text.lower())

def _tfidf_cosine(a: str, b: str) -> float:
    """Simple TF-IDF-ish cosine similarity between two text strings."""
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta or not tb:
        return 0.0
    vocab = set(ta) | set(tb)
    ca, cb = Counter(ta), Counter(tb)
    dot = sum(ca[w] * cb[w] for w in vocab)
    mag_a = math.sqrt(sum(v*v for v in ca.values()))
    mag_b = math.sqrt(sum(v*v for v in cb.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)

def _exact_overlap_score(list_a: List[str], list_b: List[str]) -> float:
    """Jaccard-like overlap for skill lists."""
    if not list_a or not list_b:
        return 0.0
    set_a = set(a.lower() for a in list_a)
    set_b = set(b.lower() for b in list_b)
    intersection = set_a & set_b
    return len(intersection) / len(set_a)

# ── Curated skill taxonomy ───────────────────────────────────────────────────
TECHNICAL_SKILLS = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
        "rust", "kotlin", "swift", "scala", "ruby", "php", "r", "matlab", "perl",
        "bash", "shell", "powershell", "dart", "lua", "haskell", "elixir",
    ],
    "frameworks_libraries": [
        "react", "vue", "angular", "next.js", "nuxt", "svelte", "django", "flask",
        "fastapi", "spring", "spring boot", "express", "node.js", "nestjs", "laravel",
        "rails", "ruby on rails", "asp.net", ".net", "pytorch", "tensorflow", "keras",
        "scikit-learn", "sklearn", "hugging face", "transformers", "langchain",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly", "opencv",
        "xgboost", "lightgbm", "catboost", "spacy", "nltk", "celery", "fastify",
        "graphql", "grpc", "tailwind", "bootstrap", "material ui", "chakra ui",
        "redux", "zustand", "mobx", "rxjs",
    ],
    "databases": [
        "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "firebase", "supabase", "oracle", "sql server",
        "neo4j", "influxdb", "clickhouse", "snowflake", "bigquery",
    ],
    "cloud": [
        "aws", "azure", "gcp", "google cloud", "ec2", "s3", "lambda", "rds",
        "ecs", "eks", "fargate", "cloudfront", "route53", "sqs", "sns", "sagemaker",
        "azure devops", "azure functions", "google kubernetes engine", "gke",
        "cloud run", "cloud functions", "heroku", "vercel", "netlify", "render",
        "digitalocean", "linode",
    ],
    "devops_tools": [
        "docker", "kubernetes", "k8s", "helm", "terraform", "ansible", "jenkins",
        "gitlab ci", "github actions", "circleci", "travis ci", "argocd", "prometheus",
        "grafana", "elk", "elasticsearch", "logstash", "kibana", "nginx", "apache",
        "linux", "unix", "git", "ci/cd", "devops", "mlops",
    ],
    "data_ai": [
        "machine learning", "deep learning", "neural networks", "nlp",
        "natural language processing", "computer vision", "reinforcement learning",
        "llm", "large language model", "generative ai", "rag", "retrieval augmented generation",
        "time series", "recommendation systems", "a/b testing", "etl",
        "data pipeline", "feature engineering", "model deployment", "mlflow",
        "airflow", "dbt", "spark", "hadoop", "kafka", "data warehousing",
        "business intelligence", "tableau", "power bi", "looker", "data studio",
    ],
    "other_technical": [
        "rest api", "restful", "microservices", "system design", "oop",
        "object oriented", "functional programming", "algorithms", "data structures",
        "sql", "nosql", "api design", "websockets", "oauth", "jwt", "ssl/tls",
        "agile", "scrum", "kanban", "jira", "confluence", "figma", "postman",
        "swagger", "openapi", "unit testing", "integration testing", "tdd",
        "bdd", "selenium", "pytest", "jest", "mocha", "blockchain", "web3",
        "solidity", "ios", "android", "react native", "flutter",
    ],
    "soft_skills": [
        "communication", "teamwork", "leadership", "problem solving", "critical thinking",
        "time management", "project management", "collaboration", "adaptability",
        "creativity", "analytical thinking", "presentation", "mentoring", "conflict resolution",
    ],
    "certifications": [
        "aws certified", "azure certified", "gcp certified", "google certified",
        "pmp", "scrum master", "cissp", "ceh", "ccna", "ccnp", "tensorflow developer",
        "databricks certified", "oracle certified", "comptia",
    ],
}

# Flat sets for fast lookup
ALL_KNOWN_SKILLS: set = set()
for category in TECHNICAL_SKILLS.values():
    ALL_KNOWN_SKILLS.update(category)

# Words that should NEVER be treated as skills
NOISE_WORDS = {
    "ability", "approach", "traditional", "highly", "potential", "genuine", "environment",
    "experience", "knowledge", "understanding", "proficiency", "familiarity", "exposure",
    "background", "expertise", "skill", "skills", "ability", "work", "worked", "working",
    "help", "helped", "helping", "participate", "participated", "involvement", "various",
    "multiple", "different", "several", "many", "strong", "good", "great", "excellent",
    "outstanding", "proven", "demonstrated", "solid", "deep", "extensive", "broad",
    "years", "year", "months", "month", "team", "company", "organization", "business",
    "role", "position", "job", "career", "industry", "sector", "field", "area",
    "project", "projects", "task", "tasks", "responsibility", "responsibilities",
    "process", "processes", "system", "systems", "solution", "solutions", "product",
    "service", "services", "technology", "technologies", "tool", "tools", "platform",
    "application", "applications", "software", "hardware", "data", "information",
    "management", "development", "design", "analysis", "implementation", "support",
    "testing", "deployment", "maintenance", "integration", "architecture",
    "requirements", "documentation", "communication", "collaboration", "other",
    "including", "using", "used", "use", "build", "built", "create", "created",
    "develop", "developed", "implement", "implemented", "new", "existing", "current",
    "based", "related", "relevant", "required", "preferred", "ideal", "candidate",
    "looking", "seeking", "must", "should", "will", "can", "able", "need",
}

# Strong vs weak action verbs
STRONG_VERBS = {
    "developed", "designed", "implemented", "engineered", "architected", "built",
    "created", "deployed", "optimized", "automated", "led", "managed", "launched",
    "reduced", "increased", "improved", "accelerated", "streamlined", "transformed",
    "delivered", "pioneered", "established", "scaled", "mentored", "spearheaded",
    "revamped", "refactored", "integrated", "migrated", "modernized", "secured",
    "analyzed", "researched", "evaluated", "proposed", "coordinated", "collaborated",
    "trained", "published", "presented", "achieved", "exceeded", "generated",
}

WEAK_VERBS = {
    "worked", "helped", "assisted", "participated", "involved", "contributed",
    "supported", "used", "utilized", "learned", "gained", "was responsible",
    "was part of", "was involved", "served as", "acted as", "handled",
}


# ── Skill Extraction ─────────────────────────────────────────────────────────

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract only meaningful skills from text. Never returns noise words.
    Uses multi-word matching against curated taxonomy.
    """
    text_lower = text.lower()
    found = set()

    # Multi-word first (greedy match longer phrases)
    for skill in sorted(ALL_KNOWN_SKILLS, key=len, reverse=True):
        # Word-boundary aware search
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)

    # Filter noise
    found = {s for s in found if s not in NOISE_WORDS and len(s) > 2}
    return sorted(found)


def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """Categorize a flat list of skills into taxonomy buckets."""
    result: Dict[str, List[str]] = {k: [] for k in TECHNICAL_SKILLS}
    uncategorized = []
    
    for skill in skills:
        placed = False
        for cat, cat_skills in TECHNICAL_SKILLS.items():
            if skill in cat_skills:
                result[cat].append(skill)
                placed = True
                break
        if not placed:
            uncategorized.append(skill)
    
    result["other"] = uncategorized
    return {k: v for k, v in result.items() if v}  # drop empty


# ── Semantic Similarity ───────────────────────────────────────────────────────

def semantic_similarity(texts_a: List[str], texts_b: List[str]) -> float:
    """
    Compute max-pooled semantic similarity between two lists of text strings.
    Uses sentence-transformers if available, TF-IDF cosine otherwise.
    Returns score 0-1.
    """
    if not texts_a or not texts_b:
        return 0.0

    model = get_model()
    if model is not None:
        try:
            from sentence_transformers import util as st_util
            emb_a = model.encode(texts_a, convert_to_tensor=True)
            emb_b = model.encode(texts_b, convert_to_tensor=True)
            cos_scores = st_util.cos_sim(emb_a, emb_b)
            best_per_a = cos_scores.max(dim=1).values
            return float(best_per_a.mean())
        except Exception:
            pass

    # TF-IDF fallback
    scores = []
    for a in texts_a:
        best = max(_tfidf_cosine(a, b) for b in texts_b)
        scores.append(best)
    return sum(scores) / len(scores)


def find_semantic_matches(
    jd_skills: List[str],
    resume_skills: List[str],
    threshold: float = 0.55,
) -> Tuple[List[Dict], List[str]]:
    """
    Returns:
        matched: list of {jd_skill, resume_match, score}
        missing: jd skills with no good match

    Uses sentence-transformers embeddings if available, TF-IDF otherwise.
    TF-IDF threshold is lower since scores are generally lower.
    """
    if not jd_skills or not resume_skills:
        return [], list(jd_skills)

    model = get_model()
    effective_threshold = threshold

    if model is not None:
        try:
            from sentence_transformers import util as st_util
            emb_jd = model.encode(jd_skills, convert_to_tensor=True)
            emb_res = model.encode(resume_skills, convert_to_tensor=True)
            cos_scores = st_util.cos_sim(emb_jd, emb_res)

            matched, missing = [], []
            for i, jd_skill in enumerate(jd_skills):
                best_idx = int(cos_scores[i].argmax())
                best_score = float(cos_scores[i][best_idx])
                if best_score >= effective_threshold:
                    matched.append({
                        "jd_skill": jd_skill,
                        "resume_match": resume_skills[best_idx],
                        "score": round(best_score, 3),
                    })
                else:
                    missing.append(jd_skill)
            return matched, missing
        except Exception:
            pass

    # ── TF-IDF fallback ──────────────────────────────────────────────────────
    # Lower threshold for TF-IDF (scores naturally lower)
    effective_threshold = 0.20
    matched, missing = [], []
    for jd_skill in jd_skills:
        best_score = 0.0
        best_match = resume_skills[0]
        for res_skill in resume_skills:
            s = _tfidf_cosine(jd_skill, res_skill)
            if s > best_score:
                best_score = s
                best_match = res_skill
        # Also check exact substring match
        jd_lower = jd_skill.lower()
        res_lower_list = [r.lower() for r in resume_skills]
        exact = jd_lower in res_lower_list or any(jd_lower in r for r in res_lower_list)
        if exact:
            best_score = max(best_score, 0.9)
            best_match = next((r for r in resume_skills if jd_skill.lower() in r.lower()), best_match)

        if best_score >= effective_threshold:
            matched.append({
                "jd_skill": jd_skill,
                "resume_match": best_match,
                "score": round(min(best_score, 1.0), 3),
            })
        else:
            missing.append(jd_skill)

    return matched, missing


# ── JD Parsing ───────────────────────────────────────────────────────────────

def parse_jd_structured(jd_text: str) -> Dict:
    """
    Parse a JD into structured JSON using taxonomy matching.
    Never includes noise words.
    """
    text_lower = jd_text.lower()
    result = {
        "technical_skills": [],
        "programming_languages": [],
        "frameworks": [],
        "databases": [],
        "cloud": [],
        "devops_tools": [],
        "data_ai_skills": [],
        "soft_skills": [],
        "certifications": [],
        "education": [],
        "domain": [],
        "responsibilities": [],
    }
    
    # Extract by category
    for lang in TECHNICAL_SKILLS["programming_languages"]:
        if re.search(r'\b' + re.escape(lang) + r'\b', text_lower):
            result["programming_languages"].append(lang)
    
    for fw in TECHNICAL_SKILLS["frameworks_libraries"]:
        if re.search(r'\b' + re.escape(fw) + r'\b', text_lower):
            result["frameworks"].append(fw)
    
    for db in TECHNICAL_SKILLS["databases"]:
        if re.search(r'\b' + re.escape(db) + r'\b', text_lower):
            result["databases"].append(db)
    
    for cloud in TECHNICAL_SKILLS["cloud"]:
        if re.search(r'\b' + re.escape(cloud) + r'\b', text_lower):
            result["cloud"].append(cloud)
    
    for tool in TECHNICAL_SKILLS["devops_tools"]:
        if re.search(r'\b' + re.escape(tool) + r'\b', text_lower):
            result["devops_tools"].append(tool)
    
    for skill in TECHNICAL_SKILLS["data_ai"]:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            result["data_ai_skills"].append(skill)
    
    for skill in TECHNICAL_SKILLS["other_technical"]:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            result["technical_skills"].append(skill)
    
    for skill in TECHNICAL_SKILLS["soft_skills"]:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            result["soft_skills"].append(skill)
    
    for cert in TECHNICAL_SKILLS["certifications"]:
        if re.search(r'\b' + re.escape(cert) + r'\b', text_lower):
            result["certifications"].append(cert)
    
    # Education detection
    edu_patterns = [
        r"bachelor['\s]s?|b\.?s\.?|b\.?e\.?|b\.?tech",
        r"master['\s]s?|m\.?s\.?|m\.?e\.?|m\.?tech",
        r"phd|ph\.d|doctorate",
        r"computer science|cs|information technology|it|software engineering",
        r"data science|mathematics|statistics|electrical engineering",
    ]
    for pat in edu_patterns:
        match = re.search(pat, text_lower)
        if match:
            result["education"].append(match.group(0).strip())
    result["education"] = list(set(result["education"]))
    
    # Domain detection
    domain_map = {
        "fintech": ["fintech", "finance", "banking", "payment", "trading"],
        "healthtech": ["health", "medical", "healthcare", "clinical", "pharma"],
        "ecommerce": ["ecommerce", "e-commerce", "retail", "marketplace"],
        "edtech": ["education", "edtech", "learning", "e-learning"],
        "cybersecurity": ["security", "cybersecurity", "infosec", "penetration"],
        "saas": ["saas", "b2b", "b2c", "enterprise software"],
        "gaming": ["gaming", "game", "unity", "unreal"],
        "blockchain": ["blockchain", "web3", "defi", "nft", "crypto"],
        "iot": ["iot", "embedded", "firmware", "hardware"],
        "ai/ml": ["artificial intelligence", "machine learning", "ai startup", "ml platform"],
    }
    for domain, keywords in domain_map.items():
        for kw in keywords:
            if kw in text_lower:
                result["domain"].append(domain)
                break
    result["domain"] = list(set(result["domain"]))
    
    # Responsibilities: extract bullet points / sentences with strong action words
    lines = [l.strip() for l in jd_text.split('\n') if l.strip()]
    for line in lines:
        if len(line) > 20 and any(
            re.search(r'\b' + v + r'\b', line.lower())
            for v in ["build", "develop", "design", "implement", "create", "manage",
                      "lead", "optimize", "maintain", "collaborate", "analyze", "deploy"]
        ):
            result["responsibilities"].append(line[:200])
    result["responsibilities"] = result["responsibilities"][:10]
    
    # Deduplicate all lists
    for key in result:
        if isinstance(result[key], list):
            seen = set()
            deduped = []
            for item in result[key]:
                if item not in seen:
                    seen.add(item)
                    deduped.append(item)
            result[key] = deduped
    
    return result


def get_all_jd_skills(jd_parsed: Dict) -> List[str]:
    """Flatten parsed JD into a flat skill list."""
    skills = []
    for key in ["technical_skills", "programming_languages", "frameworks",
                "databases", "cloud", "devops_tools", "data_ai_skills"]:
        skills.extend(jd_parsed.get(key, []))
    return list(set(skills))


# ── Resume Quality ────────────────────────────────────────────────────────────

def analyze_action_verbs(text: str) -> Dict:
    """Detect strong/weak action verbs in resume text."""
    text_lower = text.lower()
    found_strong = []
    found_weak = []
    
    for verb in STRONG_VERBS:
        if re.search(r'\b' + verb + r'\b', text_lower):
            found_strong.append(verb)
    
    for verb in WEAK_VERBS:
        if re.search(r'\b' + verb.replace(' ', r'\s+') + r'\b', text_lower):
            found_weak.append(verb)
    
    return {
        "strong_verbs": found_strong,
        "weak_verbs": found_weak,
        "strong_count": len(found_strong),
        "weak_count": len(found_weak),
    }


def detect_quantified_achievements(text: str) -> Dict:
    """Detect bullet points with quantified impact."""
    patterns = [
        r'\d+\s*%',           # percentages
        r'\$[\d,]+[kmb]?',    # dollar amounts
        r'\d+[xX]',           # multipliers
        r'\d+\s*(?:million|billion|thousand|k)\b',
        r'reduced.{0,40}\d+',
        r'increased.{0,40}\d+',
        r'improved.{0,40}\d+',
        r'saved.{0,40}\$',
        r'\d+\+?\s*(?:users|customers|clients|teams)',
    ]
    
    lines = text.split('\n')
    quantified = []
    unquantified = []
    
    for line in lines:
        line = line.strip()
        if len(line) < 20:
            continue
        # Only check lines that look like bullet achievements
        if any(re.search(r'\b' + v + r'\b', line.lower()) for v in STRONG_VERBS | WEAK_VERBS):
            if any(re.search(p, line, re.IGNORECASE) for p in patterns):
                quantified.append(line[:200])
            else:
                if len(line) < 300:
                    unquantified.append(line[:200])
    
    return {
        "quantified": quantified[:5],
        "unquantified": unquantified[:5],
        "quantification_rate": len(quantified) / max(len(quantified) + len(unquantified), 1),
    }


# ── Project Scoring ───────────────────────────────────────────────────────────

def score_projects(projects: List[Dict], jd_skills: List[str]) -> Dict:
    """Score projects for complexity, tech relevance, and impact."""
    if not projects:
        return {"score": 0, "details": []}

    total_score = 0
    details = []
    jd_lower = set(s.lower() for s in jd_skills)

    for proj in projects:
        name = proj.get("name", "")
        desc = proj.get("description", "")
        tech = proj.get("technologies", [])
        full_text = f"{name} {desc} {' '.join(tech)}".lower()

        # Tech overlap: check both explicit tech list AND text mentions
        proj_skills = set(t.lower() for t in tech)
        # Also extract skills from description text
        from nlp_utils import extract_skills_from_text
        desc_skills = set(extract_skills_from_text(full_text))
        all_proj_skills = proj_skills | desc_skills

        if jd_lower:
            tech_overlap = len(all_proj_skills & jd_lower) / len(jd_lower)
        else:
            tech_overlap = 0.3

        # Complexity signals
        complexity_kw = [
            "distributed","scalable","real-time","ml","ai","deployed","production",
            "api","microservice","cloud","billion","million","users","automated",
            "pipeline","algorithm","end-to-end","recommendation","neural",
        ]
        complexity = min(sum(1 for kw in complexity_kw if kw in full_text) / 5, 1.0)

        # Impact signals
        impact_patterns = [r'\d+%', r'\d+x', r'\$\d+', r'\d+\s*users', r'production', r'\d+,\d+']
        impact = min(sum(1 for p in impact_patterns if re.search(p, full_text, re.I)) / 3, 1.0)

        proj_score = (tech_overlap * 0.45 + complexity * 0.35 + impact * 0.20) * 100

        details.append({
            "name": name[:60],
            "score": round(proj_score),
            "tech_relevance": round(tech_overlap * 100),
            "complexity": round(complexity * 100),
            "impact": round(impact * 100),
        })
        total_score += proj_score

    avg_score = total_score / len(projects)
    return {"score": round(avg_score), "details": details}


# ── Career Fit Prediction ─────────────────────────────────────────────────────

CAREER_PROFILES = {
    "Software Engineer": {
        "core": ["python", "java", "javascript", "c++", "algorithms", "data structures", "system design", "git"],
        "bonus": ["react", "node.js", "docker", "sql", "rest api", "microservices"],
    },
    "AI/ML Engineer": {
        "core": ["python", "machine learning", "deep learning", "pytorch", "tensorflow", "scikit-learn", "nlp"],
        "bonus": ["llm", "rag", "mlops", "sql", "docker", "data pipeline", "airflow"],
    },
    "Data Scientist": {
        "core": ["python", "machine learning", "statistics", "sql", "pandas", "numpy", "scikit-learn"],
        "bonus": ["r", "tableau", "power bi", "spark", "a/b testing", "data pipeline"],
    },
    "Data Analyst": {
        "core": ["sql", "python", "excel", "tableau", "power bi", "data visualization", "statistics"],
        "bonus": ["r", "business intelligence", "looker", "snowflake", "bigquery"],
    },
    "Cloud Engineer": {
        "core": ["aws", "azure", "gcp", "terraform", "docker", "kubernetes", "linux", "networking"],
        "bonus": ["ansible", "helm", "ci/cd", "monitoring", "security"],
    },
    "DevOps Engineer": {
        "core": ["docker", "kubernetes", "ci/cd", "jenkins", "github actions", "linux", "terraform", "ansible"],
        "bonus": ["prometheus", "grafana", "aws", "python", "bash"],
    },
}

def predict_career_fit(resume_skills: List[str]) -> List[Dict]:
    """Predict percentage match for different career roles."""
    skills_lower = [s.lower() for s in resume_skills]
    results = []
    
    for role, profile in CAREER_PROFILES.items():
        core_match = sum(1 for s in profile["core"] if s in skills_lower) / len(profile["core"])
        bonus_match = sum(1 for s in profile["bonus"] if s in skills_lower) / max(len(profile["bonus"]), 1)
        fit = (core_match * 0.75 + bonus_match * 0.25) * 100
        results.append({"role": role, "fit": round(fit)})
    
    return sorted(results, key=lambda x: x["fit"], reverse=True)
