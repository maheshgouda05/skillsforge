# SkillForge – Frontend Architecture & Components

The SkillForge frontend is built with high-performance **HTML5, CSS3, and Vanilla JavaScript (ES6+)**. It requires zero client-side bundlers, compilation steps, or heavy framework runtimes, delivering an instant-loading, accessible, and reactive user experience.

---

## 📁 Directory & File Catalog

```
frontend/
├── index.html              # Modern SaaS landing page with platform preview & CTA
├── auth.html               # Dual sign-in & registration with integrated password recovery flow
├── reset-password.html     # Dedicated standalone password reset page with token prefill
├── dashboard.html          # Student dashboard hosting all career modules
├── css/
│   ├── style.css           # Global design system, CSS custom properties, utility classes
│   ├── auth.css            # Scoped authentication card and recovery flow styles
│   └── dashboard.css       # Layout scaffolding, sidebar, topbar, and reactive cards
└── js/
    ├── api.js              # Centralized Fetch API client with Bearer JWT & localStorage sync
    ├── dashboard.js        # Main dashboard controller, hash routing, metric charts & user sync
    ├── resume.js           # Drag-and-drop file uploader, tag cloud editor & gap analysis trigger
    ├── assessment.js       # 20-MCQ technical exam engine, countdown timer, question palette
    ├── roadmap.js          # 14-week personalized curriculum renderer & daily task checklist
    └── adaptive.js         # Weekly quiz validator and adaptive learning plan updater
```

---

## 🎨 Design System & Visual Identity

The interface adheres to a modern SaaS aesthetic tailored for enterprise-grade hackathon presentations:
* **Backgrounds:** Clean light gray and white canvas (`#f8fafc`, `#ffffff`).
* **Typography:** Dark navy slate hierarchy (`#0f172a`, `#1e293b`, `#334155`).
* **Primary Accents:** Royal Blue (`#2563eb`) and Deep Violet (`#6366f1`).
* **Status Badges:** Emerald Green for verified/completed tasks (`#10b981`), Amber Orange for warnings and skill gaps (`#f59e0b`).
* **Responsive Layout:** Fluid CSS Flexbox and Grid layouts optimized for mobile, tablet, and widescreen desktop displays.

---

## ⚙️ Client-Side Modules & Responsibilities

### 1. `api.js` (Unified HTTP & State Layer)
* Centralized wrapper for `fetch()` handling headers, JWT Bearer tokens, and structured error responses.
* Session management:
  * `API.getToken()` / `API.setToken(token)` / `API.clearToken()`
  * `API.getUser()` / `API.setUser(user)`
* Toast notification dispatcher: `showToast(message, type)`.

### 2. `dashboard.js` (Routing & Orchestration)
* Single-Page Application (SPA) tab switching via URL hash routing (`switchTab('resume')`).
* User profile display synchronization across the topbar active role badge, sidebar, and dashboard welcome banner.
* Radar chart rendering for skill competency visualization.
* Metric aggregation for target role match %, strong skills count, and roadmap task progress.

### 3. `resume.js` (Document Upload & Skills Management)
* Drag-and-drop file ingestion supporting PDF, DOCX, and TXT (up to 5MB).
* Interactive skill tag cloud allowing students to add custom skills or remove false detections.
* Global Target Job Role selector (`#resume-target-role`) that synchronizes the selected role across all modules and updates the Supabase database.

### 4. `assessment.js` (20-MCQ Technical Exam)
* Automatically determines the student's target role and domain based on their saved profile and extracted resume skills.
* Timed 25-minute evaluation with real-time countdown timer.
* Interactive question palette supporting direct question jumping and review flagging.
* Submits answers to `/api/assessment/submit` for instant grading and displays question-by-question explanations.

### 5. `roadmap.js` (14-Week Curriculum & Task Tracking)
* Renders a progressive 14-week learning curriculum (70 tasks across fundamentals, architecture, scale, capstones, and interview prep).
* Interactive checkboxes calling `/api/planner/task/toggle` with immediate persistence to Supabase.

### 6. `adaptive.js` (Weekly Feedback Loop)
* Administers focused 5-question weekly quizzes to validate concept mastery.
* Ingests quiz results into `/api/planner/adapt` to dynamically adjust subsequent weeks' learning materials and resources.
