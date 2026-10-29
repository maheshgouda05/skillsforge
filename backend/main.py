"""Skills-to-Job Planner - Core FastAPI Application.
Full REST API supporting authentication, resume analysis, AI skill extraction,
20-MCQ technical assessments, personalized roadmaps, adaptive weekly tests, and dashboard.
"""

import json
import os
import random
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Core local modules
from skills import (
    JOB_ROLES,
    SKILLS_TAXONOMY,
    SKILL_CATEGORIES,
    extract_skills_from_text,
    analyze_skill_gap,
    normalize_skill,
    get_role_skills,
)
from resume_parser import parse_resume_file, extract_resume_metadata
from question_bank import (
    QUESTION_BANK,
    get_questions_for_role,
    get_questions_for_skills,
    public_question,
)
from planner import (
    build_personalized_roadmap,
    toggle_task_completion,
    adapt_roadmap_from_weekly_test,
)
from ai_service import (
    analyze_resume_with_ai,
    generate_ai_adaptive_recommendation,
    is_gemini_available,
)
from database import (
    get_supabase,
    create_auth_client,
    verify_bearer_token,
    require_authenticated_user,
    db_insert,
    db_update,
    db_get,
    db_get_user_records,
)
from schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserProfileUpdateRequest,
    ResumeAnalyzeManualRequest,
    AssessmentGenerateRequest,
    AssessmentSubmitRequest,
    PlannerGenerateRequest,
    TaskToggleRequest,
    PlannerAdaptRequest,
    WeeklyTestGenerateRequest,
    WeeklyTestSubmitRequest,
)

app = FastAPI(
    title="Skills-to-Job Planner API",
    description="AI-powered career readiness, resume skill extraction, 20-MCQ technical assessments, personalized roadmaps, and adaptive learning.",
    version="2.0.0",
)

# Enable CORS for local static server and dev environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session caches for instant fallback & quick lookups
IN_MEMORY_ASSESSMENTS: Dict[str, dict] = {}
IN_MEMORY_WEEKLY_TESTS: Dict[str, dict] = {}
IN_MEMORY_PLANS: Dict[str, dict] = {}
IN_MEMORY_ANALYSES: Dict[str, dict] = {}


# -------------------- HEALTH & SYSTEM ENDPOINTS --------------------

@app.get("/")
def root():
    return {
        "name": "Skills-to-Job Planner API",
        "version": "2.0.0",
        "status": "operational",
        "docs_url": "/docs",
        "gemini_enabled": is_gemini_available(),
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gemini_active": is_gemini_available(),
    }


@app.get("/api/supabase-health")
def supabase_health():
    client = get_supabase()
    try:
        client.table("profiles").select("id").limit(1).execute()
        return {
            "status": "healthy",
            "database": "Supabase PostgreSQL",
            "message": "Connected and verified query execution."
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Supabase query check failed: {str(exc)}"
        )


@app.get("/api/roles")
def get_supported_roles():
    """Return all supported career roles, required core skills, and details."""
    roles_list = []
    for title, data in JOB_ROLES.items():
        roles_list.append({
            "title": title,
            "category": data.get("category", "Engineering"),
            "description": data.get("description", ""),
            "core_skills": data.get("core_skills", []),
            "secondary_skills": data.get("secondary_skills", []),
            "recommended_projects": data.get("recommended_projects", [])
        })
    return {"roles": roles_list}


# -------------------- AUTHENTICATION ENDPOINTS --------------------

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(request: UserRegisterRequest):
    """Register a new student in Supabase Auth and initialize user profile."""
    client = get_supabase()
    email = request.email.strip().lower()
    full_name = request.full_name.strip()
    target_role = request.target_role or "Full Stack Developer"

    user_id = None
    email_confirmed = False
    signup_session = None

    try:
        # 1. Primary Strategy: Create user via Supabase Auth Admin (pre-confirms email)
        try:
            admin_resp = client.auth.admin.create_user({
                "email": email,
                "password": request.password,
                "email_confirm": True,
                "user_metadata": {
                    "full_name": full_name,
                    "target_role": target_role,
                }
            })
            if admin_resp and admin_resp.user:
                user_id = str(admin_resp.user.id)
                email_confirmed = True
        except Exception as admin_err:
            admin_msg = str(admin_err).lower()
            # If user already registered, propagate immediately to avoid masking
            if "already" in admin_msg or "email_exists" in admin_msg or "unique" in admin_msg:
                raise admin_err

            print(f"Admin create_user notice ({admin_err}); trying standard public sign_up fallback...")
            # 2. Secondary Fallback: Standard Supabase Public Sign Up
            signup_resp = client.auth.sign_up({
                "email": email,
                "password": request.password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "target_role": target_role
                    }
                }
            })
            if signup_resp and signup_resp.user:
                user_id = str(signup_resp.user.id)
                signup_session = getattr(signup_resp, "session", None)
                if signup_resp.user.email_confirmed_at:
                    email_confirmed = True
            else:
                raise admin_err

        if not user_id:
            raise HTTPException(status_code=400, detail="Could not create user account in Supabase Auth.")

        # 3. Ensure user record exists in profiles table
        from database import ensure_profile_exists
        ensure_profile_exists(
            profile_id=user_id,
            email=email,
            full_name=full_name,
            target_role=target_role
        )

        # 4. Acquire access token for session
        access_token = None
        if signup_session and signup_session.access_token:
            access_token = signup_session.access_token

        if not access_token:
            auth_client = create_auth_client()
            for attempt in range(2):
                try:
                    sign_in_res = auth_client.auth.sign_in_with_password({
                        "email": email,
                        "password": request.password
                    })
                    if sign_in_res and sign_in_res.session:
                        access_token = sign_in_res.session.access_token
                        break
                except Exception as sign_in_err:
                    err_str = str(sign_in_err).lower()
                    if "not confirmed" in err_str:
                        # Email confirmation required by Supabase project settings
                        return {
                            "message": "Registration successful! A verification email has been sent. Please confirm your email address before signing in.",
                            "email_confirmation_required": True,
                            "access_token": None,
                            "user": {
                                "id": user_id,
                                "email": email,
                                "full_name": full_name,
                                "target_role": target_role
                            }
                        }
                    if attempt == 0:
                        import time
                        time.sleep(0.5)

        # 5. Local session fallback if socket was reset by network
        if not access_token:
            import jwt, time
            now = time.time()
            access_token = jwt.encode(
                {"sub": user_id, "email": email, "exp": int(now + 86400), "user_metadata": {"full_name": full_name, "target_role": target_role}},
                "fallback_secret",
                algorithm="HS256"
            )
            from database import TOKEN_CACHE
            TOKEN_CACHE[access_token] = {
                "user": {"id": user_id, "email": email, "user_metadata": {"full_name": full_name, "target_role": target_role}},
                "timestamp": now
            }

        return {
            "message": "User registered successfully",
            "access_token": access_token,
            "email_confirmation_required": False,
            "user": {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "target_role": target_role
            }
        }

    except Exception as exc:
        msg = str(exc)
        msg_lower = msg.lower()
        if ("already" in msg_lower and "registered" in msg_lower) or "email_exists" in msg_lower or "unique" in msg_lower:
            raise HTTPException(
                status_code=400,
                detail="A user with this email address is already registered. Please log in."
            )
        elif "password" in msg_lower and ("least" in msg_lower or "short" in msg_lower or "weak" in msg_lower):
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 6 characters long."
            )
        elif "email" in msg_lower and ("valid" in msg_lower or "format" in msg_lower or "invalid" in msg_lower):
            raise HTTPException(
                status_code=400,
                detail="Please provide a valid email address."
            )
        elif "rate limit" in msg_lower:
            raise HTTPException(
                status_code=429,
                detail="Email rate limit exceeded. Please wait a few moments before trying again."
            )
        elif "not allowed" in msg_lower:
            raise HTTPException(
                status_code=400,
                detail="Signups are not permitted by Supabase project settings. Please check Supabase Dashboard -> Authentication -> Providers -> Email -> 'Allow new users to sign up'."
            )
        raise HTTPException(
            status_code=400,
            detail=f"Registration error: {msg}"
        )


@app.post("/api/auth/login")
def login_user(request: UserLoginRequest):
    """Authenticate student with email/password and return session token & profile."""
    client = get_supabase()
    email = request.email.strip().lower()

    try:
        auth_client = create_auth_client()
        sign_in_res = auth_client.auth.sign_in_with_password({
            "email": email,
            "password": request.password
        })

        user_id = str(sign_in_res.user.id)
        
        # Fetch profile
        profile = None
        try:
            prof_res = client.table("profiles").select("*").eq("id", user_id).limit(1).execute()
            if prof_res.data:
                profile = prof_res.data[0]
        except Exception:
            pass

        full_name = (
            profile.get("full_name") if profile
            else (sign_in_res.user.user_metadata or {}).get("full_name", email.split("@")[0])
        )
        target_role = (
            profile.get("target_role") if profile
            else (sign_in_res.user.user_metadata or {}).get("target_role", "Full Stack Developer")
        )

        return {
            "message": "Login successful",
            "access_token": sign_in_res.session.access_token,
            "user": {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "target_role": target_role
            }
        }

    except Exception as exc:
        msg = str(exc)
        if "not confirmed" in msg.lower():
            raise HTTPException(
                status_code=400,
                detail="Your email address has not been confirmed yet. Please check your inbox for the confirmation link, or verify your email in Supabase."
            )
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password. Please verify your credentials."
        )


@app.get("/api/auth/me")
def get_current_user_profile(user: Optional[dict] = Depends(verify_bearer_token)):
    """Retrieve verified profile of current authenticated student."""
    if not user:
        return {"authenticated": False, "user": None}

    user_id = user["id"]
    client = get_supabase()
    profile = None
    try:
        prof_res = client.table("profiles").select("*").eq("id", user_id).limit(1).execute()
        if prof_res.data:
            profile = prof_res.data[0]
    except Exception:
        pass

    return {
        "authenticated": True,
        "user": {
            "id": user_id,
            "email": user["email"],
            "full_name": profile.get("full_name") if profile else user.get("user_metadata", {}).get("full_name", "Student"),
            "target_role": profile.get("target_role") if profile else user.get("user_metadata", {}).get("target_role", "Full Stack Developer")
        }
    }


@app.put("/api/auth/profile")
def update_profile(
    request: UserProfileUpdateRequest,
    current_user: dict = Depends(require_authenticated_user)
):
    """Update student profile preferences such as full name or target role."""
    client = get_supabase()
    user_id = current_user["id"]
    update_data = {}
    if request.full_name is not None:
        update_data["full_name"] = request.full_name.strip()
    if request.target_role is not None:
        update_data["target_role"] = request.target_role.strip()

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update.")

    try:
        client.table("profiles").update(update_data).eq("id", user_id).execute()
        return {"message": "Profile updated successfully", "updated": update_data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(exc)}")


# -------------------- RESUME ANALYSIS & SKILL EXTRACTION --------------------

@app.post("/api/resume/parse")
async def parse_resume_endpoint(resume: UploadFile = File(...)):
    """
    Parse an uploaded resume file (PDF, DOCX, TXT), extract plain text,
    metadata, and detected technical skills. Allows students to preview and edit.
    """
    if not resume.filename:
        raise HTTPException(status_code=400, detail="File must have a valid filename.")

    content = await resume.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Resume file exceeds 5MB size limit.")

    raw_text = parse_resume_file(resume.filename, content)
    metadata = extract_resume_metadata(raw_text)

    return {
        "filename": resume.filename,
        "file_size_bytes": len(content),
        "raw_text_preview": metadata["raw_text_preview"],
        "metadata": metadata,
        "detected_skills": metadata["extracted_skills"]
    }


@app.post("/api/analyze")
async def analyze_skills_endpoint(
    target_role: str = Form(...),
    job_description: str = Form(default=""),
    candidate_skills: str = Form(default=""),
    hours_per_week: int = Form(default=8),
    resume: Optional[UploadFile] = File(default=None),
    current_user: Optional[dict] = Depends(verify_bearer_token)
):
    """
    Comprehensive resume & target job skill gap analysis:
    1. Extracts or merges candidate skills
    2. Runs Gemini AI analysis (or high-fidelity heuristic fallback)
    3. Analyzes skill gaps (Strong, Intermediate, Weak, Missing)
    4. Computes transparent matching percentage
    5. Generates initial personalized learning plan
    6. Persists analysis and plan in Supabase
    """
    if not 1 <= hours_per_week <= 60:
        raise HTTPException(status_code=400, detail="Study hours must be between 1 and 60 hours/week.")

    skills_list = []
    if candidate_skills.strip():
        try:
            parsed = json.loads(candidate_skills)
            if isinstance(parsed, list):
                skills_list.extend(str(s).strip() for s in parsed if s)
        except json.JSONDecodeError:
            skills_list.extend(s.strip() for s in candidate_skills.split(",") if s.strip())

    resume_text = ""
    if resume is not None and resume.filename:
        content = await resume.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Resume file exceeds 5MB limit.")
        if content:
            resume_text = parse_resume_file(resume.filename, content)
            resume_skills = extract_skills_from_text(resume_text)
            skills_list.extend(resume_skills)

    # Normalize candidate skills
    candidate_skills_unique = sorted(list({normalize_skill(s) for s in skills_list if s.strip()}))

    # Run AI Analysis
    ai_insights = analyze_resume_with_ai(
        resume_text=resume_text or " ".join(candidate_skills_unique),
        target_role=target_role,
        candidate_skills=candidate_skills_unique
    )

    # Perform Skill Gap Comparison
    gap_analysis = analyze_skill_gap(
        candidate_skills=candidate_skills_unique,
        target_role=target_role,
        job_description=job_description
    )

    # Generate Personalized Initial Learning Roadmap
    roadmap = build_personalized_roadmap(
        target_role=target_role,
        candidate_skills=candidate_skills_unique,
        missing_skills=[m["skill"] for m in gap_analysis["missing_skills"]],
        weak_skills=[w["skill"] for w in gap_analysis["weak_skills"]],
        hours_per_week=hours_per_week,
        total_weeks=8
    )

    analysis_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())
    profile_id = current_user["id"] if current_user else None

    response_payload = {
        "analysis_id": analysis_id,
        "plan_id": plan_id,
        "profile_id": profile_id,
        "target_role": target_role,
        "match_percentage": gap_analysis["match_percentage"],
        "candidate_skills": candidate_skills_unique,
        "strong_skills": gap_analysis["strong_skills"],
        "intermediate_skills": gap_analysis["intermediate_skills"],
        "weak_skills": gap_analysis["weak_skills"],
        "missing_skills": gap_analysis["missing_skills"],
        "all_required_skills": gap_analysis["all_required_skills"],
        "ai_insights": ai_insights,
        "recommended_projects": gap_analysis["recommended_projects"],
        "roadmap_preview": {
            "total_weeks": roadmap["total_weeks"],
            "total_tasks": roadmap["total_tasks"],
            "hours_per_week": hours_per_week
        }
    }

    # Cache in memory
    IN_MEMORY_ANALYSES[analysis_id] = response_payload
    IN_MEMORY_PLANS[plan_id] = {
        "plan_id": plan_id,
        "analysis_id": analysis_id,
        "profile_id": profile_id,
        "target_role": target_role,
        "hours_per_week": hours_per_week,
        **roadmap
    }

    # Save to Supabase
    try:
        db_insert("analyses", {
            "id": analysis_id,
            "profile_id": profile_id,
            "target_role": target_role,
            "job_description": job_description,
            "alignment_score": gap_analysis["match_percentage"],
            "result": response_payload
        })
    except Exception as exc:
        print(f"Supabase analysis insert notice: {repr(exc)}")

    try:
        db_insert("learning_plans", {
            "id": plan_id,
            "profile_id": profile_id,
            "analysis_id": analysis_id,
            "plan_type": "personalized",
            "hours_per_week": hours_per_week,
            "plan_data": IN_MEMORY_PLANS[plan_id]
        })
    except Exception as exc:
        print(f"Supabase plan insert notice: {repr(exc)}")

    return response_payload


@app.get("/api/analyses/latest")
def get_latest_analysis(current_user: Optional[dict] = Depends(verify_bearer_token)):
    """Retrieve the most recent resume analysis for the logged-in student."""
    if not current_user:
        # Return latest in-memory analysis if available
        if IN_MEMORY_ANALYSES:
            latest_id = list(IN_MEMORY_ANALYSES.keys())[-1]
            return IN_MEMORY_ANALYSES[latest_id]
        return {"has_analysis": False}

    records = db_get_user_records("analyses", current_user["id"], limit=1)
    if records:
        analysis_data = records[0]["result"]
        analysis_data["created_at"] = records[0]["created_at"]
        return {"has_analysis": True, **analysis_data}

    return {"has_analysis": False}


# -------------------- TECHNICAL ASSESSMENT MODULE (20 MCQS) --------------------

@app.post("/api/assessment/generate")
def generate_technical_assessment(
    request: AssessmentGenerateRequest,
    current_user: Optional[dict] = Depends(verify_bearer_token)
):
    """
    Generate a 20-MCQ technical assessment tailored to the target role & skills.
    Crucial: Never exposes correct answers or explanations before submission.
    """
    target_role = request.target_role or "Full Stack Developer"
    count = request.count or 20

    if request.skills and len(request.skills) > 0:
        questions = get_questions_for_skills(request.skills, count=count)
    else:
        questions = get_questions_for_role(target_role, count=count)

    assessment_id = str(uuid.uuid4())
    profile_id = current_user["id"] if current_user else None

    # Cache full question objects with answers for scoring
    IN_MEMORY_ASSESSMENTS[assessment_id] = {
        "id": assessment_id,
        "profile_id": profile_id,
        "target_role": target_role,
        "questions": questions,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending"
    }

    # Insert into Supabase
    try:
        db_insert("assessments", {
            "id": assessment_id,
            "profile_id": profile_id,
            "questions": questions,
            "answers": {},
            "results": {},
            "status": "pending"
        })
    except Exception as exc:
        print(f"Supabase assessment insert notice: {repr(exc)}")

    # Return only public questions (without correct answers)
    public_questions = [public_question(q) for q in questions]

    return {
        "assessment_id": assessment_id,
        "target_role": target_role,
        "total_questions": len(public_questions),
        "timer_minutes": max(15, len(public_questions) * 1),  # 1 min per question minimum
        "questions": public_questions,
        "instructions": "Select one answer per question. Results and explanations are provided upon final submission."
    }


@app.post("/api/assessment/submit")
def submit_technical_assessment(
    request: AssessmentSubmitRequest,
    current_user: Optional[dict] = Depends(verify_bearer_token)
):
    """
    Evaluate candidate answers, calculate overall and skill-wise breakdown,
    uncover weak and strong competencies, and save results in Supabase.
    """
    assessment_id = request.assessment_id.strip()
    stored = IN_MEMORY_ASSESSMENTS.get(assessment_id)

    if not stored:
        db_rec = db_get("assessments", assessment_id)
        if db_rec:
            stored = {
                "id": db_rec["id"],
                "profile_id": db_rec.get("profile_id"),
                "questions": db_rec["questions"],
                "status": db_rec.get("status", "pending")
            }
            IN_MEMORY_ASSESSMENTS[assessment_id] = stored
        else:
            raise HTTPException(status_code=404, detail="Assessment not found.")

    questions = stored["questions"]
    answers = request.answers

    # Detailed scoring per skill and answer review
    skill_breakdown = {}
    review_list = []
    total_correct = 0

    for q in questions:
        q_id = str(q["id"])
        skill = q.get("_skill", q.get("skill", "general"))
        correct_answer = q.get("answer")
        user_answer = answers.get(q_id)
        
        is_correct = (user_answer is not None and user_answer == correct_answer)
        if is_correct:
            total_correct += 1

        skill_breakdown.setdefault(skill, {"correct": 0, "total": 0})
        skill_breakdown[skill]["total"] += 1
        if is_correct:
            skill_breakdown[skill]["correct"] += 1

        review_list.append({
            "id": q_id,
            "skill": skill,
            "question": q["question"],
            "options": q["options"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "Review core documentation for this concept.")
        })

    total_questions = len(questions)
    overall_score_percent = round((total_correct / total_questions * 100), 1) if total_questions > 0 else 0.0

    skill_results = {}
    strong_skills = []
    intermediate_skills = []
    weak_skills = []

    for skill, data in skill_breakdown.items():
        pct = round(data["correct"] / data["total"] * 100, 1) if data["total"] > 0 else 0.0
        skill_results[skill] = {
            "correct": data["correct"],
            "total": data["total"],
            "score_percent": pct
        }
        if pct >= 75:
            strong_skills.append({"skill": skill, "score": pct})
        elif pct >= 50:
            intermediate_skills.append({"skill": skill, "score": pct})
        else:
            weak_skills.append({"skill": skill, "score": pct})

    results_payload = {
        "assessment_id": assessment_id,
        "total_questions": total_questions,
        "total_correct": total_correct,
        "overall_score_percent": overall_score_percent,
        "skill_results": skill_results,
        "strong_skills": strong_skills,
        "intermediate_skills": intermediate_skills,
        "weak_skills": weak_skills,
        "review": review_list,
        "submitted_at": datetime.now(timezone.utc).isoformat()
    }

    # Update in-memory cache
    if assessment_id in IN_MEMORY_ASSESSMENTS:
        IN_MEMORY_ASSESSMENTS[assessment_id]["status"] = "submitted"
        IN_MEMORY_ASSESSMENTS[assessment_id]["results"] = results_payload
        IN_MEMORY_ASSESSMENTS[assessment_id]["answers"] = answers

    # Update Supabase
    try:
        db_update("assessments", assessment_id, {
            "answers": answers,
            "results": results_payload,
            "status": "submitted",
            "submitted_at": results_payload["submitted_at"]
        })
    except Exception as exc:
        print(f"Supabase assessment update notice: {repr(exc)}")

    return results_payload


@app.get("/api/assessments/history")
def get_assessment_history(current_user: Optional[dict] = Depends(verify_bearer_token)):
    """Retrieve past technical assessments for student profile."""
    if not current_user:
        return {"history": []}

    records = db_get_user_records("assessments", current_user["id"], limit=10)
    history = []
    for r in records:
        if r.get("status") == "submitted" and r.get("results"):
            history.append({
                "assessment_id": r["id"],
                "score_percent": r["results"].get("overall_score_percent"),
                "total_questions": r["results"].get("total_questions"),
                "total_correct": r["results"].get("total_correct"),
                "submitted_at": r.get("submitted_at", r["created_at"])
            })
    return {"history": history}


# -------------------- PERSONALIZED ROADMAP & TASK TRACKING --------------------

@app.post("/api/planner/generate")
def generate_personalized_learning_plan(
    request: PlannerGenerateRequest,
    current_user: Optional[dict] = Depends(verify_bearer_token)
):
    """
    Generate an 8-week personalized learning curriculum based on target job,
    assessment performance, and hours of availability per week.
    """
    target_role = request.target_role or "Full Stack Developer"
    hours = request.hours_per_week or 8
    candidate_skills = request.candidate_skills or []
    profile_id = current_user["id"] if current_user else None

    # If an assessment_id was provided, incorporate evaluated skill scores
    assessment_scores = {}
    if request.assessment_id:
        stored = IN_MEMORY_ASSESSMENTS.get(request.assessment_id)
        if not stored:
            db_rec = db_get("assessments", request.assessment_id)
            if db_rec and db_rec.get("results"):
                assessment_scores = db_rec["results"].get("skill_results", {})

    gap = analyze_skill_gap(
        candidate_skills=candidate_skills,
        target_role=target_role,
        assessment_scores=assessment_scores
    )

    roadmap = build_personalized_roadmap(
        target_role=target_role,
        candidate_skills=candidate_skills,
        assessment_scores=assessment_scores,
        missing_skills=[m["skill"] for m in gap["missing_skills"]],
        weak_skills=[w["skill"] for w in gap["weak_skills"]],
        hours_per_week=hours,
        total_weeks=8
    )

    plan_id = str(uuid.uuid4())
    plan_payload = {
        "plan_id": plan_id,
        "profile_id": profile_id,
        "target_role": target_role,
        "hours_per_week": hours,
        **roadmap
    }

    IN_MEMORY_PLANS[plan_id] = plan_payload

    # Persist in Supabase
    try:
        db_insert("learning_plans", {
            "id": plan_id,
            "profile_id": profile_id,
            "plan_type": "personalized",
            "hours_per_week": hours,
            "plan_data": plan_payload
        })
    except Exception as exc:
        print(f"Supabase plan insert notice: {repr(exc)}")

    return plan_payload


@app.get("/api/planner/current")
def get_current_plan(current_user: Optional[dict] = Depends(verify_bearer_token)):
    """Retrieve active learning roadmap for the student."""
    if current_user:
        records = db_get_user_records("learning_plans", current_user["id"], limit=1)
        if records:
            plan = records[0]["plan_data"]
            plan["plan_id"] = records[0]["id"]
            return {"has_plan": True, **plan}

    if IN_MEMORY_PLANS:
        latest_id = list(IN_MEMORY_PLANS.keys())[-1]
        return {"has_plan": True, **IN_MEMORY_PLANS[latest_id]}

    return {"has_plan": False}


@app.post("/api/planner/task/toggle")
def toggle_task_endpoint(
    request: TaskToggleRequest,
    current_user: Optional[dict] = Depends(verify_bearer_token)
):
    """
    Toggle task completion status (checked/unchecked) and persist immediately
    so task progress remains saved across browser refreshes.
    """
    plan_id = request.plan_id.strip()
    plan_data = IN_MEMORY_PLANS.get(plan_id)

    if not plan_data:
        db_rec = db_get("learning_plans", plan_id)
        if db_rec and db_rec.get("plan_data"):
            plan_data = db_rec["plan_data"]
            IN_MEMORY_PLANS[plan_id] = plan_data
        else:
            raise HTTPException(status_code=404, detail="Learning plan not found.")

    updated_plan = toggle_task_completion(plan_data, request.task_id, request.completed)
    IN_MEMORY_PLANS[plan_id] = updated_plan

    # Persist updated roadmap in Supabase
    try:
        db_update("learning_plans", plan_id, {
            "plan_data": updated_plan
        })
    except Exception as exc:
        print(f"Supabase task toggle update notice: {repr(exc)}")

    return {
        "plan_id": plan_id,
        "task_id": request.task_id,
        "completed": request.completed,
        "total_tasks": updated_plan["total_tasks"],
        "completed_tasks": updated_plan["completed_tasks"],
        "completion_percentage": updated_plan["completion_percentage"]
    }


# -------------------- WEEKLY TESTS & ADAPTIVE LEARNING --------------------

@app.post("/api/weekly-test/generate")
def generate_weekly_test_endpoint(
    request: WeeklyTestGenerateRequest,
    current_user: Optional[dict] = Depends(verify_bearer_token)
):
    """Generate 5 targeted MCQs for a specific skill and week."""
    skill = normalize_skill(request.skill)
    count = request.count or 5

    questions = get_questions_for_skills([skill], count=count)
    test_id = str(uuid.uuid4())
    profile_id = current_user["id"] if current_user else None

    test_meta = {
        "id": test_id,
        "profile_id": profile_id,
        "skill": skill,
        "week": request.week,
        "questions": questions,
        "status": "pending"
    }
    IN_MEMORY_WEEKLY_TESTS[test_id] = test_meta

    # Insert into Supabase
    try:
        db_insert("weekly_tests", {
            "id": test_id,
            "profile_id": profile_id,
            "skill": skill,
            "week": request.week,
            "questions": questions,
            "answers": {},
            "status": "pending"
        })
    except Exception as exc:
        print(f"Supabase weekly test insert notice: {repr(exc)}")

    return {
        "test_id": test_id,
        "skill": skill,
        "week": request.week,
        "total_questions": len(questions),
        "questions": [public_question(q) for q in questions]
    }


@app.post("/api/weekly-test/submit")
def submit_weekly_test_endpoint(
    request: WeeklyTestSubmitRequest,
    current_user: Optional[dict] = Depends(verify_bearer_token)
):
    """Evaluate weekly test, calculate score, and prepare adaptive recommendations."""
    test_id = request.test_id.strip()
    stored = IN_MEMORY_WEEKLY_TESTS.get(test_id)

    if not stored:
        db_rec = db_get("weekly_tests", test_id)
        if db_rec:
            stored = {
                "id": db_rec["id"],
                "skill": db_rec["skill"],
                "week": db_rec["week"],
                "questions": db_rec["questions"],
                "status": db_rec.get("status", "pending")
            }
            IN_MEMORY_WEEKLY_TESTS[test_id] = stored
        else:
            raise HTTPException(status_code=404, detail="Weekly test not found.")

    questions = stored["questions"]
    answers = request.answers
    correct_count = 0
    review = []

    for q in questions:
        q_id = str(q["id"])
        correct_ans = q.get("answer")
        user_ans = answers.get(q_id)
        is_corr = (user_ans is not None and user_ans == correct_ans)
        if is_corr:
            correct_count += 1
        review.append({
            "id": q_id,
            "question": q["question"],
            "options": q["options"],
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_corr,
            "explanation": q.get("explanation", "")
        })

    score_pct = round((correct_count / len(questions) * 100), 1) if questions else 0.0

    # Generate adaptive feedback
    adaptive_recommendation = generate_ai_adaptive_recommendation(
        skill=stored["skill"],
        score=score_pct,
        week=stored["week"]
    )

    # Update Supabase
    try:
        db_update("weekly_tests", test_id, {
            "answers": answers,
            "score_percent": score_pct,
            "status": "submitted",
            "submitted_at": datetime.now(timezone.utc).isoformat()
        })
    except Exception as exc:
        print(f"Supabase weekly test update notice: {repr(exc)}")

    return {
        "test_id": test_id,
        "skill": stored["skill"],
        "week": stored["week"],
        "score_percent": score_pct,
        "correct_count": correct_count,
        "total_questions": len(questions),
        "review": review,
        "adaptive_recommendation": adaptive_recommendation
    }


@app.post("/api/planner/adapt")
def adapt_planner_endpoint(
    request: PlannerAdaptRequest,
    current_user: Optional[dict] = Depends(verify_bearer_token)
):
    """
    Adaptively adjust future weeks of the roadmap based on weekly assessment results.
    Preserves completed weeks and checked-off tasks without overwriting history.
    """
    plan_id = request.plan_id.strip()
    plan_data = IN_MEMORY_PLANS.get(plan_id)

    if not plan_data:
        db_rec = db_get("learning_plans", plan_id)
        if db_rec and db_rec.get("plan_data"):
            plan_data = db_rec["plan_data"]
            IN_MEMORY_PLANS[plan_id] = plan_data
        else:
            raise HTTPException(status_code=404, detail="Learning plan not found.")

    score = request.score_percent
    skill = request.skill

    if request.test_id:
        test = IN_MEMORY_WEEKLY_TESTS.get(request.test_id)
        if not test:
            t_rec = db_get("weekly_tests", request.test_id)
            if t_rec:
                test = t_rec
        if test:
            score = test.get("score_percent", score)
            skill = test.get("skill", skill)

    if score is None or not skill:
        raise HTTPException(
            status_code=400,
            detail="Valid test_id or score_percent and skill must be provided for adaptive planning."
        )

    updated_plan = adapt_roadmap_from_weekly_test(
        plan_data=plan_data,
        completed_week=request.completed_week,
        test_skill=skill,
        score_percent=score
    )

    IN_MEMORY_PLANS[plan_id] = updated_plan

    # Update in Supabase
    try:
        db_update("learning_plans", plan_id, {
            "plan_data": updated_plan
        })
    except Exception as exc:
        print(f"Supabase adaptive plan update notice: {repr(exc)}")

    return {
        "message": f"Successfully adapted Week {request.completed_week + 1} curriculum based on {skill.title()} score ({score:.0f}%).",
        "plan_id": plan_id,
        "plan": updated_plan
    }


# -------------------- DASHBOARD AGGREGATOR --------------------

@app.get("/api/dashboard")
def get_student_dashboard(current_user: Optional[dict] = Depends(verify_bearer_token)):
    """
    Aggregate authentic data from Supabase for the student dashboard:
    Profile, target job, skill matching %, strong/weak/missing skills,
    assessment scores, roadmap completion, and recent activities.
    No hardcoded sample statistics.
    """
    profile_id = current_user["id"] if current_user else None
    user_name = "Student"
    user_email = ""
    target_role = "Full Stack Developer"

    if current_user:
        user_email = current_user["email"]
        client = get_supabase()
        try:
            p_res = client.table("profiles").select("*").eq("id", profile_id).limit(1).execute()
            if p_res.data:
                user_name = p_res.data[0].get("full_name") or user_name
                target_role = p_res.data[0].get("target_role") or target_role
        except Exception:
            pass

    # 1. Fetch Latest Resume Analysis
    latest_analysis = None
    if profile_id:
        records = db_get_user_records("analyses", profile_id, limit=1)
        if records:
            latest_analysis = records[0]["result"]
    if not latest_analysis and IN_MEMORY_ANALYSES:
        for a in reversed(list(IN_MEMORY_ANALYSES.values())):
            if not profile_id or a.get("profile_id") == profile_id or a.get("profile_id") is None:
                latest_analysis = a
                break

    # 2. Fetch Latest Assessment
    latest_assessment = None
    if profile_id:
        ass_records = db_get_user_records("assessments", profile_id, limit=1)
        if ass_records and ass_records[0].get("status") == "submitted":
            latest_assessment = ass_records[0].get("results")
    if not latest_assessment and IN_MEMORY_ASSESSMENTS:
        for a in reversed(list(IN_MEMORY_ASSESSMENTS.values())):
            if a.get("status") == "submitted" and (not profile_id or a.get("profile_id") == profile_id or a.get("profile_id") is None):
                latest_assessment = a.get("results", a)
                break

    # 3. Fetch Active Learning Plan
    active_plan = None
    if profile_id:
        plan_records = db_get_user_records("learning_plans", profile_id, limit=1)
        if plan_records:
            active_plan = plan_records[0].get("plan_data")
    if not active_plan and IN_MEMORY_PLANS:
        for p in reversed(list(IN_MEMORY_PLANS.values())):
            if not profile_id or p.get("profile_id") == profile_id or p.get("profile_id") is None:
                active_plan = p
                break

    # Build real recent activity list
    recent_activity = []
    if latest_analysis:
        recent_activity.append({
            "type": "resume_analyzed",
            "title": f"Analyzed Resume for {latest_analysis.get('target_role', target_role)}",
            "detail": f"Skill match score: {latest_analysis.get('match_percentage', 0)}%",
            "time": "Recent"
        })
    if latest_assessment:
        recent_activity.append({
            "type": "assessment_completed",
            "title": "Completed Technical Assessment",
            "detail": f"Scored {latest_assessment.get('overall_score_percent', 0)}% across {latest_assessment.get('total_questions', 20)} questions",
            "time": "Recent"
        })
    if active_plan:
        done_cnt = active_plan.get("completed_tasks", 0)
        tot_cnt = active_plan.get("total_tasks", 0)
        recent_activity.append({
            "type": "roadmap_active",
            "title": f"Active Roadmap: {active_plan.get('target_role', target_role)}",
            "detail": f"{done_cnt} of {tot_cnt} tasks completed ({active_plan.get('completion_percentage', 0)}%)",
            "time": "In Progress"
        })

    # Recommended projects for target role
    role_meta = JOB_ROLES.get(target_role, {})
    recommended_projects = role_meta.get("recommended_projects", [
        {
            "title": f"Production-Grade {target_role} Capstone",
            "difficulty": "Intermediate",
            "description": "Develop and deploy an end-to-end project applying all core and modern practices for this role."
        }
    ])

    return {
        "user": {
            "full_name": user_name,
            "email": user_email,
            "target_role": target_role
        },
        "has_resume": bool(latest_analysis),
        "has_assessment": bool(latest_assessment),
        "has_roadmap": bool(active_plan),
        "match_percentage": latest_analysis.get("match_percentage", 0.0) if latest_analysis else None,
        "strong_skills": latest_analysis.get("strong_skills", []) if latest_analysis else [],
        "intermediate_skills": latest_analysis.get("intermediate_skills", []) if latest_analysis else [],
        "weak_skills": latest_analysis.get("weak_skills", []) if latest_analysis else [],
        "missing_skills": latest_analysis.get("missing_skills", []) if latest_analysis else [],
        "assessment_score": latest_assessment.get("overall_score_percent") if latest_assessment else None,
        "assessment_skills": latest_assessment.get("skill_results", {}) if latest_assessment else {},
        "roadmap_completion": active_plan.get("completion_percentage", 0.0) if active_plan else None,
        "completed_tasks": active_plan.get("completed_tasks", 0) if active_plan else 0,
        "total_tasks": active_plan.get("total_tasks", 0) if active_plan else 0,
        "plan_id": active_plan.get("plan_id") if active_plan else None,
        "recent_activity": recent_activity,
        "recommended_projects": recommended_projects
    }
