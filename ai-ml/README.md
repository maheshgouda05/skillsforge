# SkillForge – AI/ML Models, Adaptive Learning & Career Engine

SkillForge incorporates Google's **Gemini AI API** alongside deterministic NLP and heuristics to deliver an intelligent, personalized career guidance system.

---

## 🧠 Core AI/ML Components

```
backend/
├── skills.py            # Gemini AI client, prompt templates & keyword parsing
├── question_bank.py     # Balanced question generation, difficulty rating & answer masking
├── planner.py           # 14-week progressive curriculum engine (70 daily learning tasks)
└── adaptive.py          # Real-time adaptive learning algorithm based on weekly evaluation
```

---

## 🎯 1. Resume Parsing & Skill Alignment Engine

* **Document Ingestion:** PyMuPDF extracts raw text streams from uploaded PDF, DOCX, and TXT files.
* **Extraction Pipeline:**
  1. **Gemini AI Parser:** Generates a clean JSON structure identifying declared programming languages, databases, cloud tools, frameworks, and years of experience.
  2. **Rule-Based Fallback Engine:** If the external Gemini API is unreachable or rate-limited, a high-precision regex keyword matcher extracts recognized technical skills across 9 engineering specializations.
* **Match Score Calculation:**
  $$\text{Match Percentage} = \min\left(100, \frac{\text{Candidate Verified Skills} \cap \text{Role Required Skills}}{\text{Role Required Skills}} \times 100\right)$$

---

## 🗺️ 2. 14-Week Personalized Curriculum Generator

The learning roadmap dynamically distributes topics from fundamental syntax to production-grade deployment over **14 sequential weeks (5 daily tasks per week = 70 tasks total)**:

| Phase | Weeks | Focus Area | Sample Deliverables |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Weeks 1–4 | Syntax, Fundamentals & Data Structures | Variables, functions, OOP, collections, complexity analysis |
| **Phase 2** | Weeks 5–8 | System Architecture & Database Design | REST APIs, PostgreSQL schemas, indexing, ORM integration |
| **Phase 3** | Weeks 9–11 | Advanced Cloud Scalability & Security | Docker containerization, asynchronous tasks, Redis caching |
| **Phase 4** | Weeks 12–13 | Production Capstone Project Build | Full-stack application deployment, CI/CD pipeline setup |
| **Phase 5** | Week 14 | Technical Interview Prep & Career Launch | Mock coding problems, system design drills, portfolio audit |

---

## 🔄 3. Adaptive Learning Engine

SkillForge adapts its curriculum in real time based on the student's weekly 5-MCQ test performance:

* **Score $< 50\%$ (Needs Reinforcement):**
  * Injects foundational tutorials, guided coding exercises, and syntax walkthroughs into the subsequent week.
  * Adjusts daily task difficulty to reinforce core prerequisites before moving to advanced topics.
* **Score $50\% - 75\%$ (Standard Progress):**
  * Keeps the target progression while inserting practical implementation drills and real-world edge cases.
* **Score $> 75\%$ (Advanced Mastery):**
  * Fast-tracks the curriculum with advanced architectural patterns, performance optimization challenges, and production scalability tasks.

---

## ⏱️ 4. Assessment Bank & Zero-Leakage Security

* Over 200+ vetted technical multiple-choice questions across languages, frameworks, web protocols, and systems.
* Questions are balanced across Easy (30%), Medium (50%), and Hard (20%) difficulty levels.
* **Answer Leakage Prevention:** Public assessment endpoints strip the correct answer index (`answer`) and technical rationale (`explanation`) before delivering questions to the frontend client. Answers are strictly preserved on the server for grading upon final submission.
