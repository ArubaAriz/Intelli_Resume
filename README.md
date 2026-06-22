#  IntelliResume - ATS Resume Intelligence Platform

An AI-powered resume analysis platform that evaluates resumes against job descriptions using semantic matching, ATS compatibility checks, experience relevance analysis, and recruiter-focused insights.

Unlike traditional keyword-based ATS checkers, IntelliResume attempts to analyze the context and relevance of skills, projects, and experience to provide more meaningful feedback.

---

## Features

### Resume Parsing

* Supports PDF and DOCX resumes
* Extracts:

  * Contact Information
  * Education
  * Skills
  * Experience
  * Projects
  * Certifications

### Job Description Analysis

* Parses job descriptions to identify:

  * Technical Skills
  * Programming Languages
  * Frameworks
  * Databases
  * Cloud Technologies
  * Soft Skills
  * Domain Requirements

### ATS Compatibility Analysis

Checks for:

* Contact information completeness
* Missing resume sections
* ATS-friendly formatting indicators
* Resume structure quality

### Semantic Skill Matching

* Compares resume skills against job requirements
* Uses NLP-based similarity techniques
* Includes fallback matching when advanced models are unavailable
* Reduces dependence on exact keyword matching

### Experience & Project Analysis

* Evaluates experience relevance against job responsibilities
* Assesses project relevance based on:

  * Technologies used
  * Complexity
  * Domain alignment

### Resume Quality Analysis

Evaluates:

* Action verbs
* Achievement-oriented language
* Quantified accomplishments
* Resume writing quality

### Recruiter Insights

Provides:

* Key strengths
* Areas for improvement
* Hiring readiness indicators

### Career Fit Analysis

Estimates alignment with roles such as:

* Software Engineer
* AI / ML Engineer
* Data Analyst
* Data Scientist
* Cloud Engineer
* DevOps Engineer

---

## Tech Stack

### Backend

* FastAPI
* SQLite
* PyMuPDF
* python-docx
* sentence-transformers
* scikit-learn

### Frontend

* React
* Tailwind CSS
* Recharts
* Vite

---

## Project Structure

```text
Intelli_Resume/

backend/
├── main.py
├── nlp_utils.py
├── resume_parser.py
├── scoring.py
├── requirements.txt

frontend/
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── package-lock.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── index.html

README.md
.gitignore
```

---

## Installation

### Backend

```bash
cd backend

pip install -r requirements.txt

python main.py
```

Backend runs on:

```text
http://localhost:8000
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

---

## API Endpoints

### Health Check

```http
GET /health
```

### Resume Analysis

```http
POST /analyze
```

Uploads:

* Resume (PDF/DOCX)
* Job Description

Returns:

* ATS Score
* Skill Analysis
* Experience Analysis
* Project Analysis
* Recruiter Insights
* Career Fit Results
* Recommendations

### Analysis History

```http
GET /history
```

```http
GET /history/{analysis_id}
```

---

## Current Limitations

* Designed for educational and portfolio purposes.
* Analysis results are heuristic estimates and should not be considered recruiter decisions.
* Career-fit and benchmarking outputs are indicative rather than predictive.
* Semantic matching quality depends on available NLP models and extracted resume content.

---

## Future Improvements

* Export analysis reports as PDF
* Resume comparison across multiple job descriptions
* Enhanced visualization dashboard
* User authentication and saved profiles
* Improved semantic matching models


