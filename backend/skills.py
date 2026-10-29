"""Skills taxonomy and role matching definitions for Skills-to-Job Planner."""

import re
from typing import Dict, List, Set, Tuple

# Supported roles and their required competencies
JOB_ROLES: Dict[str, dict] = {
    "Python Developer": {
        "title": "Python Developer",
        "category": "Backend & General Development",
        "description": "Designs, develops, tests, and deploys high-performance Python applications, backend services, REST APIs, and automated data pipelines.",
        "core_skills": ["python", "fastapi", "sql", "git", "rest apis", "docker"],
        "secondary_skills": ["data structures", "redis", "testing", "postgresql", "linux"],
        "optional_skills": ["html", "css", "javascript", "pandas", "cloud"],
        "recommended_projects": [
            {
                "title": "Asynchronous RESTful Job Queue API",
                "difficulty": "Intermediate",
                "description": "Build a scalable background job processing service with FastAPI, Redis, and Celery featuring JWT authentication and worker queues."
            },
            {
                "title": "Enterprise Microservice with PostgreSQL & Docker",
                "difficulty": "Advanced",
                "description": "Develop containerized microservices communicating via REST and message broker with full unit test coverage using Pytest."
            }
        ]
    },
    "Full Stack Developer": {
        "title": "Full Stack Developer",
        "category": "Web Engineering",
        "description": "Builds end-to-end responsive web applications spanning dynamic frontends, robust REST/GraphQL APIs, databases, and deployment infrastructure.",
        "core_skills": ["html", "css", "javascript", "react", "python", "sql", "git", "rest apis"],
        "secondary_skills": ["fastapi", "nodejs", "postgresql", "docker", "tailwind css"],
        "optional_skills": ["typescript", "data structures", "testing", "cloud"],
        "recommended_projects": [
            {
                "title": "Collaborative SaaS Project Workspace",
                "difficulty": "Advanced",
                "description": "Full-stack web app featuring real-time state synchronization, role-based access control, PostgreSQL data layer, and responsive UI."
            },
            {
                "title": "Interactive E-Commerce Platform with Analytics",
                "difficulty": "Intermediate",
                "description": "Responsive storefront with product search, shopping cart state management, checkout API, and sales metrics dashboard."
            }
        ]
    },
    "Frontend Developer": {
        "title": "Frontend Developer",
        "category": "Web Engineering",
        "description": "Crafts accessible, high-performance, and responsive user interfaces using modern HTML, CSS, JavaScript, and frontend component architectures.",
        "core_skills": ["html", "css", "javascript", "react", "git", "responsive design", "web performance"],
        "secondary_skills": ["typescript", "tailwind css", "rest apis", "testing"],
        "optional_skills": ["cloud", "docker", "python"],
        "recommended_projects": [
            {
                "title": "Interactive Real-Time Analytics Dashboard",
                "difficulty": "Intermediate",
                "description": "Build a responsive dashboard using modern CSS Grid/Flexbox, dynamic Chart.js data streams, and theme customization."
            },
            {
                "title": "Accessible Component Design System",
                "difficulty": "Advanced",
                "description": "A fully WCAG-compliant design system library containing modal, dropdown, data table, and form elements with keyboard navigation."
            }
        ]
    },
    "Backend Developer": {
        "title": "Backend Developer",
        "category": "Backend & Cloud",
        "description": "Architects server-side logic, database schemas, secure authentication mechanisms, and scalable REST APIs for high-throughput applications.",
        "core_skills": ["python", "sql", "rest apis", "git", "postgresql", "docker", "data structures"],
        "secondary_skills": ["fastapi", "redis", "system design", "linux", "testing"],
        "optional_skills": ["cloud", "nodejs", "pandas"],
        "recommended_projects": [
            {
                "title": "High-Throughput Financial Ledger API",
                "difficulty": "Advanced",
                "description": "REST API with ACID-compliant transactions, balance auditing, idempotent transfer execution, and rate limiting."
            },
            {
                "title": "Distributed Caching & Session Management Gateway",
                "difficulty": "Intermediate",
                "description": "Reverse proxy caching tier using Redis and FastAPI to optimize slow queries and manage multi-tenant user sessions."
            }
        ]
    },
    "Data Analyst": {
        "title": "Data Analyst",
        "category": "Analytics & Business Intelligence",
        "description": "Transforms raw transactional data into actionable business intelligence through SQL queries, statistical analysis, and interactive executive dashboards.",
        "core_skills": ["sql", "excel", "python", "pandas", "power bi", "statistics", "data visualization"],
        "secondary_skills": ["tableau", "numpy", "git"],
        "optional_skills": ["machine learning", "fastapi", "docker"],
        "recommended_projects": [
            {
                "title": "Customer Churn & Retention Executive Dashboard",
                "difficulty": "Intermediate",
                "description": "Analyze multi-year customer cohort retention using advanced SQL window functions and build an interactive Power BI / Tableau dashboard."
            },
            {
                "title": "Sales Forecasting & Market Basket Analysis",
                "difficulty": "Intermediate",
                "description": "Extract transaction data with Pandas, apply association rule mining, and deliver actionable inventory recommendations."
            }
        ]
    },
    "Data Scientist": {
        "title": "Data Scientist",
        "category": "Data Science & AI",
        "description": "Applies statistical modeling, exploratory data analysis, and predictive machine learning algorithms to extract predictive insights from complex datasets.",
        "core_skills": ["python", "sql", "pandas", "numpy", "statistics", "machine learning", "data visualization"],
        "secondary_skills": ["git", "testing", "docker"],
        "optional_skills": ["deep learning", "power bi", "tableau", "cloud"],
        "recommended_projects": [
            {
                "title": "Predictive Healthcare Readmission Model",
                "difficulty": "Advanced",
                "description": "End-to-end classification pipeline featuring missing data imputation, outlier detection, cross-validation, and SHAP explainability."
            },
            {
                "title": "Dynamic Housing Price Regression & EDA Report",
                "difficulty": "Intermediate",
                "description": "Exploratory data analysis uncovering collinear features followed by regularized regression (Lasso/Ridge) with automated reporting."
            }
        ]
    },
    "Machine Learning Engineer": {
        "title": "Machine Learning Engineer",
        "category": "Data Science & AI",
        "description": "Designs, trains, evaluates, optimizes, and productionizes machine learning pipelines, deep neural networks, and scalable inference services.",
        "core_skills": ["python", "machine learning", "numpy", "pandas", "statistics", "docker", "git"],
        "secondary_skills": ["deep learning", "fastapi", "sql", "data structures"],
        "optional_skills": ["cloud", "linux", "testing"],
        "recommended_projects": [
            {
                "title": "Real-Time Object Detection or NLP Inference Service",
                "difficulty": "Advanced",
                "description": "Containerized FastAPI microservice serving an optimized ONNX/PyTorch model with batching and request metrics."
            },
            {
                "title": "Automated MLOps Training & Drift Detection Pipeline",
                "difficulty": "Advanced",
                "description": "Continuous training pipeline detecting data distribution drift and automatically retraining baseline models."
            }
        ]
    },
    "AI Engineer": {
        "title": "AI Engineer",
        "category": "Modern AI & LLMs",
        "description": "Builds generative AI applications, Retrieval-Augmented Generation (RAG) architectures, autonomous agent workflows, and vector search systems.",
        "core_skills": ["python", "rest apis", "git", "machine learning", "docker", "fastapi"],
        "secondary_skills": ["prompt engineering", "rag", "sql", "data structures"],
        "optional_skills": ["deep learning", "cloud", "javascript"],
        "recommended_projects": [
            {
                "title": "Enterprise RAG Assistant with Vector Search",
                "difficulty": "Advanced",
                "description": "Build a knowledge retrieval engine using document chunking, semantic vector embeddings, and LLM synthesis with citations."
            },
            {
                "title": "Autonomous Multi-Tool Agent Workflow",
                "difficulty": "Advanced",
                "description": "Agentic system integrating custom function calling, calculator/SQL execution sandboxes, and verification loops."
            }
        ]
    },
    "Software Engineer": {
        "title": "Software Engineer",
        "category": "Core Engineering",
        "description": "Develops robust, maintainable, scalable software solutions applying core algorithms, object-oriented principles, unit testing, and version control.",
        "core_skills": ["data structures", "git", "python", "sql", "rest apis"],
        "secondary_skills": ["docker", "system design", "testing", "linux", "postgresql"],
        "optional_skills": ["javascript", "html", "css", "fastapi", "cloud"],
        "recommended_projects": [
            {
                "title": "Custom Distributed Key-Value Store",
                "difficulty": "Advanced",
                "description": "In-memory database implementing hash indexing, WAL (write-ahead logging), persistence, and TCP client protocol."
            },
            {
                "title": "High-Performance CLI Task Automation Suite",
                "difficulty": "Intermediate",
                "description": "Command-line tool suite implementing concurrent task scheduling, file integrity verification, and structured output."
            }
        ]
    }
}

# Skill extraction dictionary with variations & aliases
SKILLS_TAXONOMY: Dict[str, List[str]] = {
    "python": ["python", "python3", "python programming", "py"],
    "sql": ["sql", "structured query language", "mysql", "postgresql", "postgres", "sqlite", "tsql", "plsql"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "excel": ["excel", "microsoft excel", "spreadsheets", "vlookup", "pivot tables"],
    "statistics": ["statistics", "statistical analysis", "probability", "hypothesis testing", "regression analysis"],
    "power bi": ["power bi", "powerbi", "dax"],
    "tableau": ["tableau"],
    "machine learning": ["machine learning", "scikit-learn", "sklearn", "ml models", "supervised learning", "unsupervised learning", "classification", "clustering"],
    "deep learning": ["deep learning", "neural networks", "pytorch", "tensorflow", "keras", "cnn", "rnn", "transformers"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "sass", "scss", "flexbox", "grid"],
    "javascript": ["javascript", "js", "ecmascript", "es6"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "react.js", "reactjs"],
    "fastapi": ["fastapi", "fast api"],
    "nodejs": ["node.js", "nodejs", "node", "express", "express.js"],
    "git": ["git", "github", "gitlab", "version control"],
    "docker": ["docker", "containerization", "containers", "dockerfile"],
    "rest apis": ["rest", "restful", "rest api", "rest apis", "api development", "json api"],
    "data structures": ["data structures", "dsa", "algorithms", "problem solving"],
    "system design": ["system design", "distributed systems", "scalability", "microservices"],
    "postgresql": ["postgresql", "postgres", "pgadmin"],
    "redis": ["redis", "in-memory cache", "caching"],
    "tailwind css": ["tailwind", "tailwind css", "tailwindcss"],
    "responsive design": ["responsive design", "mobile responsive", "media queries"],
    "web performance": ["web performance", "lighthouse", "core web vitals", "lcp"],
    "testing": ["testing", "unit testing", "pytest", "jest", "qa testing"],
    "data visualization": ["data visualization", "matplotlib", "seaborn", "charts", "dashboards"],
    "prompt engineering": ["prompt engineering", "prompt design", "llm prompting"],
    "rag": ["rag", "retrieval augmented generation", "vector search"],
    "cloud": ["cloud", "aws", "gcp", "azure", "google cloud"],
    "linux": ["linux", "bash", "shell scripting", "unix"]
}

# Skill category groupings
SKILL_CATEGORIES: Dict[str, str] = {
    "python": "Programming Languages",
    "javascript": "Programming Languages",
    "typescript": "Programming Languages",
    "html": "Frontend Engineering",
    "css": "Frontend Engineering",
    "react": "Frontend Engineering",
    "tailwind css": "Frontend Engineering",
    "responsive design": "Frontend Engineering",
    "web performance": "Frontend Engineering",
    "fastapi": "Backend & APIs",
    "nodejs": "Backend & APIs",
    "rest apis": "Backend & APIs",
    "sql": "Databases & Storage",
    "postgresql": "Databases & Storage",
    "redis": "Databases & Storage",
    "pandas": "Data Analytics",
    "numpy": "Data Analytics",
    "excel": "Data Analytics",
    "power bi": "Data Analytics",
    "tableau": "Data Analytics",
    "statistics": "Data Analytics",
    "data visualization": "Data Analytics",
    "machine learning": "AI & Machine Learning",
    "deep learning": "AI & Machine Learning",
    "prompt engineering": "AI & Machine Learning",
    "rag": "AI & Machine Learning",
    "git": "DevOps & Tools",
    "docker": "DevOps & Tools",
    "linux": "DevOps & Tools",
    "cloud": "DevOps & Tools",
    "testing": "Software Craftsmanship",
    "data structures": "Core Computer Science",
    "system design": "Core Computer Science"
}


def normalize_skill(skill: str) -> str:
    """Normalize skill name to standard canonical lowercase name."""
    s = skill.strip().lower()
    for canonical, aliases in SKILLS_TAXONOMY.items():
        if s == canonical or s in aliases:
            return canonical
    return s


def extract_skills_from_text(text: str) -> List[str]:
    """Extract known technical skills from text using regex boundary matching."""
    if not text:
        return []
    normalized_text = f" {text.lower()} "
    found_skills: Set[str] = set()

    for canonical, aliases in SKILLS_TAXONOMY.items():
        for alias in aliases:
            pattern = r"(?<![a-zA-Z0-9_\-\.])" + re.escape(alias.lower()) + r"(?![a-zA-Z0-9_\-\.])"
            if re.search(pattern, normalized_text):
                found_skills.add(canonical)
                break

    return sorted(list(found_skills))


def get_role_skills(role_name: str) -> Tuple[List[str], List[str]]:
    """Retrieve core and secondary skills for a given role name, with custom fallback."""
    if role_name in JOB_ROLES:
        role_info = JOB_ROLES[role_name]
        return role_info["core_skills"], role_info.get("secondary_skills", [])
    
    # Try case-insensitive lookup
    for name, info in JOB_ROLES.items():
        if name.lower() == role_name.lower():
            return info["core_skills"], info.get("secondary_skills", [])

    # Default general engineering skills for unknown/custom roles
    return ["python", "sql", "git", "rest apis", "data structures"], ["html", "css", "docker"]


def analyze_skill_gap(
    candidate_skills: List[str],
    target_role: str,
    job_description: str = "",
    assessment_scores: dict = None
) -> dict:
    """
    Comprehensive skill gap analysis between candidate skills, assessment scores,
    and target job requirements.
    """
    candidate_set = {normalize_skill(s) for s in candidate_skills if s.strip()}
    core_skills, secondary_skills = get_role_skills(target_role)

    # If job description is provided, extract additional job skills
    extra_job_skills = set()
    if job_description.strip():
        extra_job_skills = set(extract_skills_from_text(job_description))

    all_required_set = set(core_skills) | set(secondary_skills) | extra_job_skills
    if not all_required_set:
        all_required_set = {"python", "sql", "git", "rest apis"}

    assessment_scores = assessment_scores or {}

    strong_skills = []
    intermediate_skills = []
    weak_skills = []
    missing_skills = []

    for skill in sorted(all_required_set):
        norm_s = normalize_skill(skill)
        has_skill = norm_s in candidate_set
        
        # Check assessment score if available
        score_info = assessment_scores.get(norm_s) or assessment_scores.get(skill)
        score_val = None
        if isinstance(score_info, dict) and "score_percent" in score_info:
            score_val = score_info["score_percent"]
        elif isinstance(score_info, (int, float)):
            score_val = float(score_info)

        if score_val is not None:
            if score_val >= 75:
                strong_skills.append({"skill": norm_s, "score": score_val, "category": SKILL_CATEGORIES.get(norm_s, "General")})
            elif score_val >= 50:
                intermediate_skills.append({"skill": norm_s, "score": score_val, "category": SKILL_CATEGORIES.get(norm_s, "General")})
            else:
                weak_skills.append({"skill": norm_s, "score": score_val, "category": SKILL_CATEGORIES.get(norm_s, "General")})
        elif has_skill:
            # Candidate has it on resume, but has not taken assessment yet
            intermediate_skills.append({"skill": norm_s, "score": 65.0, "category": SKILL_CATEGORIES.get(norm_s, "General"), "source": "resume"})
        else:
            missing_skills.append({"skill": norm_s, "category": SKILL_CATEGORIES.get(norm_s, "General")})

    # Transparent Match Score Calculation
    # Core skills weight: 2.0, Secondary/Extra skills weight: 1.0
    total_weight = 0.0
    earned_weight = 0.0

    for skill in all_required_set:
        norm_s = normalize_skill(skill)
        w = 2.0 if norm_s in core_skills else 1.0
        total_weight += w

        score_info = assessment_scores.get(norm_s)
        if isinstance(score_info, dict) and "score_percent" in score_info:
            earned_weight += w * (score_info["score_percent"] / 100.0)
        elif norm_s in candidate_set:
            earned_weight += w * 0.75  # Resume mention gives 75% baseline credit

    match_percentage = round((earned_weight / total_weight * 100), 1) if total_weight > 0 else 0.0
    match_percentage = min(100.0, max(0.0, match_percentage))

    role_info = JOB_ROLES.get(target_role, {})
    recommended_projects = role_info.get("recommended_projects", [
        {
            "title": f"Production-Grade {target_role} Capstone",
            "difficulty": "Intermediate",
            "description": "Develop and deploy an end-to-end project applying all core and modern practices for this role."
        }
    ])

    return {
        "target_role": target_role,
        "match_percentage": match_percentage,
        "strong_skills": strong_skills,
        "intermediate_skills": intermediate_skills,
        "weak_skills": weak_skills,
        "missing_skills": missing_skills,
        "all_required_skills": sorted(list(all_required_set)),
        "candidate_skills": sorted(list(candidate_set)),
        "recommended_projects": recommended_projects
    }

