# SkillForge – Backend REST API & Service Architecture

The SkillForge backend is a high-performance RESTful service built with **Python 3.10+ and FastAPI**, powered by **Supabase PostgreSQL & GoTrue Authentication** and Google's **Gemini AI API**.

---

## 📁 Backend Directory Structure

```
backend/
├── main.py              # Main FastAPI application, routing, dependency injection & CORS
├── database.py          # Supabase client factory, session isolation & JWT verification
├── schemas.py           # Pydantic v2 schemas for request validation & API contracts
├── skills.py            # Taxonomy of 9 engineering specializations & keyword parser
├── question_bank.py     # 20-MCQ question bank, difficulty balancing & security masking
├── planner.py           # 14-week progressive curriculum generator & daily task tracking
└── adaptive.py          # Dynamic plan adaptation engine based on quiz feedback
```

---

## 🚀 Running the Backend Service

```bash
# Set Python path to backend directory and start Uvicorn
PYTHONPATH=backend python3 -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Interactive documentation is automatically generated and accessible at:
* **Swagger UI:** `http://localhost:8000/docs`
* **ReDoc:** `http://localhost:8000/redoc`

---

## 📑 API Endpoint Catalog

### 1. System & Roles
* `GET /` – Service health, version, and Gemini status.
* `GET /api/health` – Lightweight uptime check.
* `GET /api/supabase-health` – Validates PostgreSQL read connectivity.
* `GET /api/roles` – Returns the 9 supported engineering roles and skill matrices.

### 2. Authentication & Student Profile
* `POST /api/auth/register` – Creates a student account in Supabase Auth & inserts a linked profile.
* `POST /api/auth/login` – Authenticates credentials and returns a Bearer access token.
* `POST /api/auth/forgot-password` – Initiates password recovery via Supabase Auth admin API.
* `POST /api/auth/reset-password` – Verifies recovery OTP and updates user password in Supabase.
* `GET /api/auth/me` – Retrieves verified student profile from JWT token.
* `PUT /api/auth/profile` – Updates user preferences (full name, target role).

### 3. Resume & Skill Extraction
* `POST /api/resume/parse` – Ingests PDF/DOCX/TXT resumes and extracts skills via PyMuPDF.
* `POST /api/analyze` – Performs comprehensive skill gap analysis using Gemini AI.
* `GET /api/analysis/latest` – Returns the student's latest skill gap report.

### 4. 20-MCQ Technical Competency Exam
* `POST /api/assessment/generate` – Generates 20 balanced MCQs. Automatically determines target role from student profile if omitted. Correct answers are stripped before response.
* `POST /api/assessment/submit` – Grades submitted answers and returns score and explanations.
* `GET /api/assessment/{id}` – Fetches past assessment results.

### 5. 14-Week Personalized Curriculum & Tasks
* `POST /api/planner/generate` – Generates a tailored 14-week (70 daily tasks) curriculum.
* `GET /api/planner/current` – Retrieves the student's active roadmap and completed task states.
* `POST /api/planner/task/toggle` – Checks/unchecks a daily learning task with immediate Supabase persistence.
* `POST /api/planner/adapt` – Re-optimizes upcoming curriculum weeks based on quiz results.

### 6. Weekly Adaptive Assessments
* `POST /api/weekly-test/generate` – Generates a targeted 5-MCQ quiz on a weekly skill.
* `POST /api/weekly-test/submit` – Evaluates quiz and triggers adaptive curriculum recommendations.

### 7. Dashboard Aggregator
* `GET /api/dashboard` – Single-call endpoint aggregating target role match %, strong skills count, skill gaps count, roadmap completion %, recent activity, and recommended capstone projects.
