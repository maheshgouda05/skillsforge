"""Pydantic schemas for request and response validation in Skills-to-Job Planner."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, EmailStr


# -------------------- AUTH SCHEMAS --------------------

class UserRegisterRequest(BaseModel):
    email: str = Field(..., min_length=4, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    target_role: Optional[str] = Field(default="Full Stack Developer")


class UserLoginRequest(BaseModel):
    email: str = Field(...)
    password: str = Field(...)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token_or_otp: str = Field(..., min_length=4, max_length=128)
    new_password: str = Field(..., min_length=6, max_length=100)


class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    target_role: Optional[str] = None


# -------------------- RESUME & SKILL SCHEMAS --------------------

class ResumeAnalyzeManualRequest(BaseModel):
    target_role: str = Field(default="Full Stack Developer")
    job_description: Optional[str] = Field(default="")
    candidate_skills: List[str] = Field(default_factory=list)
    hours_per_week: int = Field(default=8, ge=1, le=60)


# -------------------- ASSESSMENT SCHEMAS --------------------

class AssessmentGenerateRequest(BaseModel):
    target_role: Optional[str] = Field(default=None)
    skills: Optional[List[str]] = Field(default=None)
    count: int = Field(default=20, ge=5, le=50)


class AssessmentSubmitRequest(BaseModel):
    assessment_id: str = Field(...)
    answers: Dict[str, int] = Field(..., description="Mapping of question ID to chosen option index (0-3)")


# -------------------- PLANNER SCHEMAS --------------------

class PlannerGenerateRequest(BaseModel):
    target_role: str = Field(default="Full Stack Developer")
    hours_per_week: int = Field(default=8, ge=1, le=60)
    candidate_skills: Optional[List[str]] = Field(default_factory=list)
    assessment_id: Optional[str] = Field(default=None)


class TaskToggleRequest(BaseModel):
    plan_id: str = Field(...)
    task_id: str = Field(...)
    completed: bool = Field(...)


class PlannerAdaptRequest(BaseModel):
    plan_id: str = Field(...)
    completed_week: int = Field(..., ge=1, le=52)
    test_id: Optional[str] = None
    skill: Optional[str] = None
    score_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)


# -------------------- WEEKLY TEST SCHEMAS --------------------

class WeeklyTestGenerateRequest(BaseModel):
    skill: str = Field(..., min_length=1)
    week: int = Field(default=1, ge=1, le=52)
    count: int = Field(default=5, ge=1, le=20)


class WeeklyTestSubmitRequest(BaseModel):
    test_id: str = Field(...)
    answers: Dict[str, int] = Field(...)


# -------------------- PLACEMENT & HIRING HUB SCHEMAS --------------------

class TrackApplicationRequest(BaseModel):
    opportunity_id: str = Field(...)
    status: str = Field(default="Interested", description="Interested, Preparing, Applied, Assessment Completed, Interview Scheduled, Selected, Rejected")
    applied_date: Optional[str] = None
    interview_date: Optional[str] = None
    notes: Optional[str] = ""


class OpportunityPrepareRequest(BaseModel):
    student_skills: Optional[List[str]] = Field(default=None)


class OpportunityCreateRequest(BaseModel):
    company_name: str = Field(...)
    company_short: Optional[str] = None
    company_logo: Optional[str] = ""
    role_title: str = Field(...)
    job_type: str = Field(default="Full-time")
    location: str = Field(default="Pan India")
    package_ctc: str = Field(default="Not specified")
    eligibility_criteria: str = Field(...)
    required_skills: List[str] = Field(default_factory=list)
    selection_rounds: List[Dict[str, Any]] = Field(default_factory=list)
    opening_date: Optional[str] = "Open now"
    deadline_date: Optional[str] = "Not specified"
    recruitment_date: Optional[str] = "Not specified"
    status: Optional[str] = "Currently Open"
    apply_url: str = Field(...)
    source_url: Optional[str] = None
    is_verified: Optional[bool] = True


class OpportunityUpdateRequest(BaseModel):
    company_name: Optional[str] = None
    company_short: Optional[str] = None
    company_logo: Optional[str] = None
    role_title: Optional[str] = None
    job_type: Optional[str] = None
    location: Optional[str] = None
    package_ctc: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    required_skills: Optional[List[str]] = None
    selection_rounds: Optional[List[Dict[str, Any]]] = None
    opening_date: Optional[str] = None
    deadline_date: Optional[str] = None
    recruitment_date: Optional[str] = None
    status: Optional[str] = None
    apply_url: Optional[str] = None
    source_url: Optional[str] = None
    is_verified: Optional[bool] = None


