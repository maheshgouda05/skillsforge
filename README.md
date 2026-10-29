# Skills-to-Job Planner

> **AI-Powered Career Readiness & Technical Assessment Platform**  
> *Final Hackathon Submission*

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E.svg)](https://supabase.com/)
[![Google Gemini](https://img.shields.io/badge/AI-Gemini%20API-4285F4.svg)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Project Overview

**Skills-to-Job Planner** is an AI-driven, end-to-end career guidance and readiness platform designed to help students and aspiring engineers bridge the gap between their current skills and the expectations of top technology employers.

The platform guides students through an adaptive 12-stage journey:
$$\text{Register} \longrightarrow \text{Upload Resume} \longrightarrow \text{Skill Extraction} \longrightarrow \text{Target Role Selection} \longrightarrow \text{20-MCQ Exam} \longrightarrow \text{Skill Gap Analysis} \longrightarrow \text{Personalized Roadmap} \longrightarrow \text{Daily Tasks} \longrightarrow \text{Weekly Assessment} \longrightarrow \text{Adaptive Updates} \longrightarrow \text{Progress Analytics}$$

Every stage is connected to a resilient FastAPI backend and persisted securely in Supabase PostgreSQL with user-specific data isolation.

---

## 2. Core Features

### 📄 Multi-Format Resume Parser & Editor
- **Direct File Parsing**: Upload resumes in **PDF**, **DOCX**, or **TXT** format (up to 5MB).
- **Dual Skill Extractor**: Combines PyMuPDF text mining, regular expression word-boundary filters, and Google Gemini AI insights.
- **Interactive Skill Cloud**: Students can remove false positives and manually add custom skills before analysis.

### 🎯 Job Role Alignment & Skill Gap Analysis
- **9 Predefined Career Paths**:
  - Python Developer
  - Full Stack Developer
  - Frontend Developer
  - Backend Developer
  - Data Analyst
  - Data Scientist
  - Machine Learning Engineer
  - AI Engineer
  - Software Engineer
- **Custom Job Role & Description**: Paste job postings to evaluate alignment against company-specific job descriptions.
- **Competency Categorization**: Identifies **Strong Skills** ($\ge 75\%$), **Intermediate Skills** ($50\text{--}74\%$), **Weak Skills** ($< 50\%$), and **Missing Core Prerequisites**.
- **Transparent Match Score**: Weighted matching algorithm (Core competencies weighted at $2.0\times$, secondary skills at $1.0\times$).

### ⏱️ 20-MCQ Technical Assessment Module
- **20 Questions by Default**: Domain-specific multiple choice questions balanced across required role competencies.
- **Security-First Evaluation**: Correct answers and explanations are **never exposed** to the client before submission.
- **Exam Engine**: 25-minute live countdown timer, 20-button navigation palette (Answered, Flagged, Unanswered), and submit confirmation modal.
- **Detailed Explanations**: Post-submission breakdown reveals question-by-question answer keys with rationale.

### 🗺️ Dynamic 8-Week Personalized Roadmap
- **Custom Curriculum**: Structured around study availability (1 to 40 hours/week).
- **Actionable Daily Tasks**: Day 1 through Day 5 tasks with time estimates.
- **Persistent Progress**: Task checkboxes persist directly in Supabase—refreshing or switching devices preserves checked tasks.
- **Curated Educational Resources**: Direct links to official documentation, interactive sandbox exercises, and video walkthroughs.

### 🧠 Adaptive Learning & Weekly Milestones
- **Weekly Assessments**: 5-question quizzes to verify weekly retention.
- **Dynamic Curriculum Adaptation**:
  - **Remedial Path** ($< 50\%$ score): Automatically injects fundamental revision and guided debugging exercises into the upcoming week.
  - **Accelerated Path** ($\ge 80\%$ score): Elevates upcoming modules to advanced production architecture and performance tuning.
- **Non-Destructive History**: Past completed weeks and task histories remain preserved.

### 📊 Real-Time Analytics Dashboard
- **Zero Fake Statistics**: 100% of dashboard numbers, charts, and recent activity feeds are derived from real Supabase data.
- **Meaningful Empty States**: Helpful prompts guide new users when an assessment or resume upload has not yet taken place.
- **Radar Chart Visualizer**: Multi-dimensional competency chart rendered using Chart.js.

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6+) | SaaS user interface with zero heavy framework bloat |
| **Styling** | Custom SaaS CSS Design System | Responsive navy/slate/violet palette, cards, and grids |
| **Visualizations** | Chart.js (CDN) | Radar & progress charts |
| **Backend** | Python 3.11+, FastAPI, Uvicorn | High-performance asynchronous REST API |
| **Document Processing** | PyMuPDF (fitz), python-docx | Text extraction from PDF & DOCX resumes |
| **Database & Auth** | Supabase PostgreSQL, Supabase Auth | User management, RLS policies, and structured storage |
| **AI Integration** | Google Gemini API (`gemini-2.5-flash`) | Resume analysis, career coaching, and skill synthesis |

---

## 4. Folder Structure

```
hackthon3/
├── backend/
│   ├── main.py                  # Core FastAPI application & REST endpoints
│   ├── database.py              # Supabase client, auth verification, and CRUD helpers
│   ├── skills.py                # 9 career roles, 35+ skill taxonomies, and matching engine
│   ├── resume_parser.py         # PyMuPDF & python-docx resume text and metadata extractor
│   ├── question_bank.py         # 150+ categorized technical assessment questions
│   ├── planner.py               # 8-week personalized roadmap & adaptive learning engine
│   ├── ai_service.py            # Google Gemini API integration with heuristic fallbacks
│   ├── schemas.py               # Pydantic request and response models
│   ├── requirements.txt         # Pinned backend dependencies
│   ├── .env                     # Local environment credentials (git-ignored)
│   └── .env.example             # Clean environment template
├── frontend/
│   ├── index.html               # Product landing page with workflow preview
│   ├── auth.html                # Unified Login, Registration, and Evaluator Guest Access
│   ├── dashboard.html           # Core student platform (7 integrated tab views)
│   ├── css/
│   │   ├── style.css            # Global CSS variables, buttons, alerts, and badges
│   │   ├── dashboard.css        # Dashboard grids, question palette, and roadmap timeline
│   │   └── auth.css             # Authentication card layout
│   └── js/
│       ├── api.js               # Unified fetch client with Bearer auth injection & toast alerts
│       ├── resume.js            # Resume drag-and-drop, parsing, and skill tag editor
│       ├── assessment.js        # 20-MCQ test engine, timer, and question palette
│       ├── roadmap.js           # 8-week curriculum renderer with persistent task toggles
│       ├── adaptive.js          # Weekly assessment quiz and adaptive roadmap update handler
│       └── dashboard.js         # Dashboard metrics aggregator, radar chart, and profile
├── database/
│   └── supabase_schema.sql      # Complete Supabase PostgreSQL schema, RLS policies, and triggers
├── tests/
│   └── test_e2e_flow.py         # 11-step end-to-end automated verification test suite
└── README.md                    # Project documentation and execution guide
```

---

## 5. Prerequisites

Before running the application locally, ensure you have:
1. **Python 3.11 or higher** installed (`python3 --version`).
2. **Git** installed.
3. A modern web browser (Google Chrome, Firefox, Safari, or Edge).

---

## 6. Local Setup & Execution Instructions

### Step 1: Clone or Open Project Workspace
```bash
cd /Users/maheshbasarkod/Documents/hackthon3
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `backend/.env`:
```bash
cp backend/.env.example backend/.env
```
Open `backend/.env` and verify your credentials:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SECRET_KEY=your-supabase-service-role-secret-key
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.5-flash
```
*(Note: A working Supabase configuration is pre-configured in `backend/.env` for this submission).*

### Step 3: Setup Python Environment & Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Run FastAPI Backend Server
```bash
uvicorn main:app --reload --port 8000
```
- Interactive API Documentation (Swagger UI): **http://localhost:8000/docs**
- ReDoc Interface: **http://localhost:8000/redoc**
- Health Endpoint: **http://localhost:8000/api/health**

### Step 5: Run Frontend Static Server
In a separate terminal tab:
```bash
# Option A: Python Built-in Static Server
cd frontend
python3 -m http.server 5500

# Option B: VS Code Live Server
# Right click frontend/index.html -> "Open with Live Server" (Port 5500)
```
- Open in your browser: **http://localhost:5500/**
- Student Dashboard: **http://localhost:5500/dashboard.html**
- Authentication / Sign In: **http://localhost:5500/auth.html**

---

## 7. Supabase Database Configuration

The project uses Supabase PostgreSQL for persistent data storage.

### Tables
1. `profiles`: User information (`id`, `full_name`, `email`, `target_role`, `created_at`).
2. `analyses`: Resume parsing results, detected skills, and matching scores.
3. `assessments`: 20-MCQ exam questions, answers, score breakdown, and timestamps.
4. `learning_plans`: 8-week personalized roadmap data with persistent task completion states.
5. `weekly_tests`: Weekly adaptive quiz submissions and performance metrics.

### Applying Database Schema
To initialize or verify the schema on your Supabase project:
1. Open the **SQL Editor** in your [Supabase Dashboard](https://supabase.com/dashboard).
2. Paste the contents of `database/supabase_schema.sql`.
3. Click **Run**. All tables, indexes, and Row Level Security (RLS) policies will be provisioned.

---

## 8. Automated End-to-End Testing

To run the automated 11-step integration test that validates the complete student journey:
```bash
python3 tests/test_e2e_flow.py
```
**Test Results:**
```
=== STARTING FULL END-TO-END SYSTEM TEST ===
1. Testing Health Check... ✓ Backend healthy
2. Testing Supported Roles... ✓ Retrieved 9 industry roles
3. Testing User Registration / Auth... ✓ Registered test user
4. Testing /api/auth/me... ✓ Auth verification passed
5. Testing Resume & Skill Gap Analysis... ✓ Analysis complete
6. Testing 20-MCQ Technical Assessment Generation... ✓ 20 MCQs with zero answer leakage
7. Testing Assessment Submission and Grading... ✓ Assessment scored (Overall: 25.0%)
8. Testing Active Roadmap Fetch... ✓ Retrieved 8-week curriculum (40 tasks)
9. Testing Task Completion & Persistence... ✓ Task completion persisted across refresh
10. Testing Weekly Assessment & Adaptive Planning... ✓ Adaptive update preserved completed tasks
11. Testing Full Student Dashboard Aggregator... ✓ Loaded authentic Supabase metrics

=== ALL 11 END-TO-END TESTS PASSED WITH 100% SUCCESS! ===
```

---

## 9. Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| **CORS errors in browser** | Port mismatch | Ensure backend runs on port 8000 and frontend runs on port 5500. FastAPI is configured with `allow_origins=["*"]`. |
| **Resume upload rejected** | File too large or invalid format | Ensure file is PDF, DOCX, or TXT under 5MB. |
| **Gemini API key missing** | Empty `GEMINI_API_KEY` | The application includes a high-fidelity built-in heuristic AI fallback so the system remains 100% functional even without an API key. To activate live Gemini analysis, obtain a free key at [Google AI Studio](https://aistudio.google.com/) and paste it in `backend/.env`. |
| **Supabase Connection Reset** | Network socket drop | The backend includes an in-memory token cache (`TOKEN_CACHE`) and local JWT verification so network drops will not log out authenticated students. |

---

## 10. Hackathon Demonstration Guide

For live hackathon judging:
1. Navigate to **http://localhost:5500/**.
2. Click **"Launch Dashboard"** or go to `auth.html` and click **"⚡ Quick Demo Access (For Judges / Reviewers)"**.
3. In the **Resume & Skills** tab:
   - Upload any sample PDF/DOCX resume or click **"Run Complete Skill Gap Analysis"**.
   - Notice the detected skill tag cloud, role match percentage, and Gemini career coaching advice.
4. In the **Technical Exam** tab:
   - Click **"Start 20-Question Assessment"**.
   - Notice the 25-minute live timer, question palette navigation, and instant grading with detailed answer explanations.
5. In the **Learning Roadmap** tab:
   - View your customized 8-week curriculum.
   - Check off daily tasks—notice the progress bar updates and tasks stay checked even after refreshing the page!
6. In the **Weekly & Adaptive** tab:
   - Take a quick 5-question weekly quiz.
   - Click **"Apply Adaptive Changes to Roadmap"** to watch the future weeks automatically adapt based on your score without overwriting past weeks!
7. In the **Overview** tab:
   - Review your live Competency Radar Chart, real activity history, and recommended capstone projects.

