"""Personalized learning roadmap and adaptive curriculum generator."""

from typing import Dict, List, Optional
from skills import get_role_skills, normalize_skill, SKILLS_TAXONOMY, SKILL_CATEGORIES

# Curated high-value educational references for each skill
CURATED_RESOURCES: Dict[str, List[dict]] = {
    "python": [
        {"title": "Official Python Tutorial", "type": "Documentation", "url": "https://docs.python.org/3/tutorial/"},
        {"title": "Real Python Tutorials & Guides", "type": "Interactive", "url": "https://realpython.com/"},
        {"title": "FreeCodeCamp Complete Python Course", "type": "Video", "url": "https://www.youtube.com/results?search_query=freecodecamp+python+full+course"}
    ],
    "sql": [
        {"title": "PostgreSQL Official Documentation", "type": "Documentation", "url": "https://www.postgresql.org/docs/"},
        {"title": "SQLZoo Interactive Exercises", "type": "Interactive", "url": "https://sqlzoo.net/"},
        {"title": "Alex The Analyst Complete SQL Guide", "type": "Video", "url": "https://www.youtube.com/results?search_query=alex+the+analyst+sql+full+course"}
    ],
    "fastapi": [
        {"title": "FastAPI Official Interactive Tutorial", "type": "Documentation", "url": "https://fastapi.tiangolo.com/tutorial/"},
        {"title": "Building Production APIs with FastAPI", "type": "Interactive", "url": "https://fastapi.tiangolo.com/deployment/"},
        {"title": "Full Stack FastAPI & Python Walkthrough", "type": "Video", "url": "https://www.youtube.com/results?search_query=fastapi+full+course"}
    ],
    "git": [
        {"title": "Pro Git Book (Free)", "type": "Documentation", "url": "https://git-scm.com/book/en/v2"},
        {"title": "Learn Git Branching (Visualizer)", "type": "Interactive", "url": "https://learngitbranching.js.org/"},
        {"title": "Git & GitHub Crash Course", "type": "Video", "url": "https://www.youtube.com/results?search_query=git+and+github+crash+course"}
    ],
    "rest apis": [
        {"title": "RESTful API Design Best Practices", "type": "Documentation", "url": "https://restfulapi.net/"},
        {"title": "MDN HTTP Overview & Methods", "type": "Documentation", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP"},
        {"title": "API Design Masterclass", "type": "Video", "url": "https://www.youtube.com/results?search_query=rest+api+design+best+practices"}
    ],
    "javascript": [
        {"title": "JavaScript.info Modern Tutorial", "type": "Documentation", "url": "https://javascript.info/"},
        {"title": "MDN JavaScript Reference", "type": "Documentation", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"},
        {"title": "JavaScript Mastery Full Course", "type": "Video", "url": "https://www.youtube.com/results?search_query=javascript+mastery+full+course"}
    ],
    "html": [
        {"title": "MDN HTML Basics & Elements", "type": "Documentation", "url": "https://developer.mozilla.org/en-US/docs/Learn/HTML"},
        {"title": "W3C Semantic HTML Guidelines", "type": "Documentation", "url": "https://www.w3.org/WAI/fundamentals/accessibility-intro/"},
        {"title": "HTML5 Crash Course for Beginners", "type": "Video", "url": "https://www.youtube.com/results?search_query=html5+crash+course+for+beginners"}
    ],
    "css": [
        {"title": "CSS-Tricks Complete Guide to Flexbox", "type": "Documentation", "url": "https://css-tricks.com/snippets/css/a-guide-to-flexbox/"},
        {"title": "CSS Grid Garden Game", "type": "Interactive", "url": "https://cssgridgarden.com/"},
        {"title": "Kevin Powell Modern CSS Tutorials", "type": "Video", "url": "https://www.youtube.com/results?search_query=kevin+powell+modern+css"}
    ],
    "react": [
        {"title": "React.dev Official Documentation", "type": "Documentation", "url": "https://react.dev/"},
        {"title": "Full Stack Open (University of Helsinki)", "type": "Interactive", "url": "https://fullstackopen.com/en/"},
        {"title": "React 19 Complete Guide", "type": "Video", "url": "https://www.youtube.com/results?search_query=react+19+full+course"}
    ],
    "docker": [
        {"title": "Docker Get Started Documentation", "type": "Documentation", "url": "https://docs.docker.com/get-started/"},
        {"title": "Play with Docker Interactive Lab", "type": "Interactive", "url": "https://labs.play-with-docker.com/"},
        {"title": "Docker in 100 Seconds & Full Guide", "type": "Video", "url": "https://www.youtube.com/results?search_query=docker+tutorial+for+beginners"}
    ],
    "pandas": [
        {"title": "Pandas Official 10-Minute Guide", "type": "Documentation", "url": "https://pandas.pydata.org/docs/user_guide/10min.html"},
        {"title": "Kaggle Pandas Micro-Course", "type": "Interactive", "url": "https://www.kaggle.com/learn/pandas"},
        {"title": "Keith Galli Pandas Full Course", "type": "Video", "url": "https://www.youtube.com/results?search_query=keith+galli+pandas+python"}
    ],
    "machine learning": [
        {"title": "Scikit-Learn User Guide", "type": "Documentation", "url": "https://scikit-learn.org/stable/user_guide.html"},
        {"title": "Google Machine Learning Crash Course", "type": "Interactive", "url": "https://developers.google.com/machine-learning/crash-course"},
        {"title": "StatQuest with Josh Starmer", "type": "Video", "url": "https://www.youtube.com/results?search_query=statquest+machine+learning"}
    ],
    "data structures": [
        {"title": "NeetCode Roadmap & DSA Solutions", "type": "Interactive", "url": "https://neetcode.io/roadmap"},
        {"title": "GeeksforGeeks Data Structures", "type": "Documentation", "url": "https://www.geeksforgeeks.org/data-structures/"},
        {"title": "Abdul Bari Algorithms Series", "type": "Video", "url": "https://www.youtube.com/results?search_query=abdul+bari+algorithms"}
    ]
}


def get_skill_resources(skill: str) -> List[dict]:
    """Retrieve resources for a skill or build clean educational defaults."""
    norm = normalize_skill(skill)
    if norm in CURATED_RESOURCES:
        return CURATED_RESOURCES[norm]
    return [
        {
            "title": f"{skill.title()} Technical Documentation",
            "type": "Documentation",
            "url": f"https://www.google.com/search?q={skill.replace(' ', '+')}+documentation"
        },
        {"title": f"{skill.title()} Interactive Tutorials", "type": "Interactive", "url": f"https://www.google.com/search?q={skill.replace(' ', '+')}+tutorial"},
        {"title": f"{skill.title()} Video Walkthrough", "type": "Video", "url": f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial"}
    ]


def generate_weekly_daily_tasks(week_num: int, skill: str, focus_tier: str, hours_per_week: int) -> List[dict]:
    """Generate 5 actionable daily tasks for the week with estimated hours and completion state."""
    daily_hours = round(hours_per_week / 5.0, 1)

    # Week 12: Capstone Architecture & Implementation (Part 1)
    if week_num == 12:
        activities = [
            ("Day 1: Project Architecture & Spec", f"Draft architecture diagram, database entity relationships, and API contract for your {skill.title()} capstone."),
            ("Day 2: Core Domain Model & Schemas", f"Implement core data structures, Pydantic/database schemas, and business rules for {skill.title()}."),
            ("Day 3: Primary API Endpoints & Logic", f"Code the primary CRUD controllers, request validation, and error handlers using {skill.title()}."),
            ("Day 4: Service Layer & State Flow", f"Integrate external services, state persistence, and mock data pipelines."),
            ("Day 5: Mid-Sprint Code Review", f"Review implementation, run linters, write initial smoke tests, and document progress.")
        ]
    # Week 13: Capstone Polish, Testing & Deployment (Part 2)
    elif week_num == 13:
        activities = [
            ("Day 1: Frontend/Client Integration", f"Connect frontend views with backend endpoints, handling asynchronous states and loading indicators."),
            ("Day 2: Comprehensive Test Suite", f"Write unit tests and end-to-end integration tests covering edge cases and error responses."),
            ("Day 3: Containerization & Dockerfile", f"Containerize the application with Docker, multi-stage builds, and environment variables."),
            ("Day 4: Live Cloud Deployment", f"Deploy the capstone to cloud hosting, configure environment secrets, and verify live URLs."),
            ("Day 5: README & Demo Documentation", f"Write a comprehensive README with setup instructions, architecture breakdown, and demo GIF.")
        ]
    # Week 14: Portfolio Review, Technical Interview & Career Launch
    elif week_num == 14:
        activities = [
            ("Day 1: Resume & GitHub Alignment", f"Update your resume with quantitative achievements from your {skill.title()} capstone and polish your GitHub pinned repositories."),
            ("Day 2: Core Technical Interview Drill", f"Solve 5 high-frequency technical interview questions on {skill.title()} with optimal time/space complexity."),
            ("Day 3: System Design & Trade-Offs", f"Practice explaining scalability, caching, load balancing, and failure modes in software architecture."),
            ("Day 4: Behavioral & Storytelling Mock", f"Structure STAR-format responses for past technical hurdles, debugging triumphs, and team collaboration."),
            ("Day 5: Final Graduation & Roadmap Completion", f"Complete the final comprehensive assessment and graduate into active job applications.")
        ]
    elif focus_tier == "remedial":
        activities = [
            ("Day 1: Concept Fundamentals", f"Review core syntax, mental model, and common misconceptions in {skill.title()}."),
            ("Day 2: Guided Walkthroughs", f"Code along with 2 structured tutorials implementing foundational {skill.title()} examples."),
            ("Day 3: Hands-On Debugging", f"Debug and fix 5 intentional syntax and logic errors in existing {skill.title()} code snippets."),
            ("Day 4: Independent Practice", f"Build 3 isolated exercises from scratch using {skill.title()} without copy-pasting."),
            ("Day 5: Synthesis & Weekly Quiz", f"Document your learnings and complete the Week {week_num} technical assessment.")
        ]
    elif focus_tier == "advanced":
        activities = [
            ("Day 1: Advanced Patterns & Architecture", f"Explore advanced design patterns, concurrency, and performance tuning in {skill.title()}."),
            ("Day 2: Production Boilerplate Setup", f"Setup a production-grade repository using best practices, linting, and tests for {skill.title()}."),
            ("Day 3: Complex Feature Implementation", f"Implement core domain logic with edge-case handling and asynchronous processing in {skill.title()}."),
            ("Day 4: Unit Testing & Benchmark Profiling", f"Write thorough unit tests and profile performance bottlenecks in your {skill.title()} code."),
            ("Day 5: Capstone Review & Quiz", f"Perform code review, push to GitHub, and pass the Week {week_num} assessment.")
        ]
    else:  # intermediate / standard
        activities = [
            ("Day 1: Topic Overview & Documentation", f"Read official documentation and explore standard API references for {skill.title()}."),
            ("Day 2: Practical Coding Drills", f"Solve 4 practical coding challenges applying intermediate {skill.title()} methods."),
            ("Day 3: Mini-Feature Integration", f"Integrate a working component with realistic mock data using {skill.title()}."),
            ("Day 4: Refactoring & Error Handling", f"Add defensive error handling, input validation, and clean comments in {skill.title()}."),
            ("Day 5: Review & Milestone Assessment", f"Summarize key takeaways in your dev journal and take the Week {week_num} test.")
        ]

    tasks = []
    for idx, (title, desc) in enumerate(activities, 1):
        tasks.append({
            "id": f"w{week_num}_t{idx}",
            "day": f"Day {idx}",
            "title": title,
            "description": desc,
            "time_est_hours": daily_hours,
            "completed": False
        })
    return tasks


def build_personalized_roadmap(
    target_role: str,
    candidate_skills: List[str],
    assessment_scores: dict = None,
    missing_skills: List[str] = None,
    weak_skills: List[str] = None,
    hours_per_week: int = 8,
    total_weeks: int = 14
) -> dict:
    """
    Generate an in-depth 14-week personalized curriculum dynamically structured around
    target job requirements, candidate strengths, and evaluated weaknesses.
    """
    candidate_skills = candidate_skills or []
    missing_skills = missing_skills or []
    weak_skills = weak_skills or []
    assessment_scores = assessment_scores or {}

    core_skills, secondary_skills = get_role_skills(target_role)

    # Prioritize skills that need the most attention
    ordered_skills: List[str] = []
    
    # Priority 1: Evaluated weak skills (<50%)
    for w in weak_skills:
        s_norm = normalize_skill(w if isinstance(w, str) else w.get("skill", ""))
        if s_norm and s_norm not in ordered_skills:
            ordered_skills.append(s_norm)

    # Priority 2: Missing core skills
    for m in missing_skills:
        s_norm = normalize_skill(m if isinstance(m, str) else m.get("skill", ""))
        if s_norm and s_norm not in ordered_skills:
            ordered_skills.append(s_norm)

    # Priority 3: Target role core skills
    for c in core_skills:
        s_norm = normalize_skill(c)
        if s_norm not in ordered_skills:
            ordered_skills.append(s_norm)

    # Priority 4: Secondary role skills
    for sec in secondary_skills:
        s_norm = normalize_skill(sec)
        if s_norm not in ordered_skills:
            ordered_skills.append(s_norm)

    if not ordered_skills:
        ordered_skills = ["python", "sql", "git", "rest apis", "docker", "data structures", "fastapi"]

    weeks = []
    for week_num in range(1, total_weeks + 1):
        # Determine focus skill and phase
        if week_num in (12, 13):
            # Capstone weeks focus on primary core skill + project implementation
            skill = ordered_skills[0] if ordered_skills else "full stack"
            phase = "Capstone Build & Deployment"
        elif week_num == 14:
            # Interview and career launch week
            skill = ordered_skills[0] if ordered_skills else "system design"
            phase = "Technical Interview & Career Launch"
        else:
            skill = ordered_skills[(week_num - 1) % len(ordered_skills)]
            if week_num <= 4:
                phase = "Foundation & Core Prerequisites"
            elif week_num <= 8:
                phase = "Intermediate Architecture & Tools"
            else:
                phase = "Advanced Scale & Optimization"
        
        # Determine focus tier based on score
        score_info = assessment_scores.get(skill)
        score_val = None
        if isinstance(score_info, dict) and "score_percent" in score_info:
            score_val = score_info["score_percent"]
        elif isinstance(score_info, (int, float)):
            score_val = float(score_info)

        if week_num in (12, 13):
            focus_tier = "advanced"
            goal = f"Architect, build, and deploy an end-to-end production {target_role} capstone applying {skill.title()}."
        elif week_num == 14:
            focus_tier = "advanced"
            goal = f"Master technical coding interviews, system design fundamentals, and resume presentation for {target_role}."
        elif score_val is not None:
            if score_val < 50:
                focus_tier = "remedial"
                goal = f"Reinforce core concepts, syntax, and fundamental patterns in {skill.title()}."
            elif score_val >= 80:
                focus_tier = "advanced"
                goal = f"Master advanced production techniques, scalability, and complex deliverables in {skill.title()}."
            else:
                focus_tier = "standard"
                goal = f"Solidify intermediate problem-solving and practical execution in {skill.title()}."
        elif skill in missing_skills:
            focus_tier = "remedial"
            goal = f"Build foundational fluency in {skill.title()} required for {target_role}."
        else:
            focus_tier = "standard"
            goal = f"Sharpen practical proficiency and real-world application of {skill.title()}."

        daily_tasks = generate_weekly_daily_tasks(week_num, skill, focus_tier, hours_per_week)
        resources = get_skill_resources(skill)

        # Build progressive practical exercises and project deliverables
        if week_num in (12, 13):
            exercises = [
                f"Implement end-to-end user workflows with database transactions in your {target_role} project.",
                f"Configure automated CI/CD pipeline and containerized deployment scripts."
            ]
            project_title = f"Week {week_num} Capstone: Production {target_role} System (Part {week_num - 11})"
            project_desc = f"Develop and deploy a complete production-grade application demonstrating full mastery of {skill.title()} and {target_role} core competencies."
        elif week_num == 14:
            exercises = [
                f"Conduct a timed mock technical interview solving 3 algorithmic challenges.",
                f"Present a 5-minute technical walkthrough of your deployed capstone architecture."
            ]
            project_title = "Week 14 Milestone: Portfolio & Interview Readiness Dossier"
            project_desc = "Publish your live project URL, documented GitHub repository, and technical portfolio ready for recruiter submission."
        else:
            exercises = [
                f"Write a modular solution solving real-world {skill.title()} problems.",
                f"Implement automated tests verifying edge cases in your {skill.title()} code."
            ]
            project_title = f"Week {week_num} Milestone: {skill.title()} Practical Deliverable"
            project_desc = f"Build and document a self-contained code module utilizing {skill.title()} that can be showcased on your portfolio."

        weeks.append({
            "week": week_num,
            "focus_skill": skill,
            "phase": phase,
            "category": SKILL_CATEGORIES.get(skill, "General Engineering"),
            "focus_tier": focus_tier,
            "goal": goal,
            "hours_allocated": hours_per_week,
            "daily_tasks": daily_tasks,
            "resources": resources,
            "practical_exercises": exercises,
            "weekly_project": {
                "title": project_title,
                "description": project_desc
            },
            "weekly_test": {
                "skill": skill,
                "status": "pending",
                "score_percent": None
            },
            "is_completed": False
        })

    total_tasks = sum(len(w["daily_tasks"]) for w in weeks)

    return {
        "target_role": target_role,
        "total_weeks": total_weeks,
        "hours_per_week": hours_per_week,
        "total_tasks": total_tasks,
        "completed_tasks": 0,
        "completion_percentage": 0.0,
        "weeks": weeks
    }


def toggle_task_completion(plan_data: dict, task_id: str, is_completed: bool) -> dict:
    """
    Toggle a specific task completion status and recalculate roadmap metrics.
    Preserves all other tasks and historical weeks.
    """
    weeks = plan_data.get("weeks", [])
    found = False

    for week in weeks:
        week_all_done = True
        for task in week.get("daily_tasks", []):
            if task.get("id") == task_id:
                task["completed"] = is_completed
                found = True
            if not task.get("completed", False):
                week_all_done = False
        week["is_completed"] = week_all_done

    total_tasks = sum(len(w.get("daily_tasks", [])) for w in weeks)
    completed_tasks = sum(
        1 for w in weeks for t in w.get("daily_tasks", []) if t.get("completed", False)
    )

    plan_data["total_tasks"] = total_tasks
    plan_data["completed_tasks"] = completed_tasks
    plan_data["completion_percentage"] = (
        round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0.0
    )

    return plan_data


def adapt_roadmap_from_weekly_test(
    plan_data: dict,
    completed_week: int,
    test_skill: str,
    score_percent: float
) -> dict:
    """
    Adaptively update future weeks of the roadmap based on weekly assessment results.
    Preserves completed weeks (1..completed_week) and their task completion statuses!
    """
    weeks = plan_data.get("weeks", [])
    hours_per_week = plan_data.get("hours_per_week", 8)

    # 1. Update the weekly test status on the completed week
    for w in weeks:
        if w.get("week") == completed_week:
            w["weekly_test"] = {
                "skill": test_skill,
                "status": "submitted",
                "score_percent": score_percent
            }

    # 2. Modify upcoming week (completed_week + 1) based on score
    next_week_num = completed_week + 1
    for w in weeks:
        if w.get("week") == next_week_num:
            if score_percent < 50:
                # Student struggled: Inject revision and reinforcement
                w["focus_tier"] = "remedial"
                w["focus_skill"] = test_skill  # Continue working on this skill for revision
                w["goal"] = f"Urgent revision & reinforcement in {test_skill.title()} following recent quiz score ({score_percent:.0f}%)."
                w["daily_tasks"] = generate_weekly_daily_tasks(next_week_num, test_skill, "remedial", hours_per_week)
                w["practical_exercises"].insert(0, f"Revision drill: Re-solve missed concepts in {test_skill.title()} step-by-step.")
                w["adaptive_note"] = f"Adjusted to provide intensive practice in {test_skill.title()} based on week {completed_week} evaluation."
            elif score_percent >= 80:
                # Student excelled: Accelerate to advanced topics
                w["focus_tier"] = "advanced"
                w["goal"] = f"Accelerated mastery: Deep dive into production architectures & performance for {w['focus_skill'].title()}."
                w["daily_tasks"] = generate_weekly_daily_tasks(next_week_num, w["focus_skill"], "advanced", hours_per_week)
                w["adaptive_note"] = f"Accelerated learning path triggered by exceptional {test_skill.title()} score ({score_percent:.0f}%)."
            break

    # Recalculate tasks and metrics
    total_tasks = sum(len(w.get("daily_tasks", [])) for w in weeks)
    completed_tasks = sum(
        1 for w in weeks for t in w.get("daily_tasks", []) if t.get("completed", False)
    )

    plan_data["total_tasks"] = total_tasks
    plan_data["completed_tasks"] = completed_tasks
    plan_data["completion_percentage"] = (
        round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0.0
    )

    return plan_data
