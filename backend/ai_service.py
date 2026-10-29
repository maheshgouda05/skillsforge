"""Gemini API integration with robust heuristics fallback for Skills-to-Job Planner."""

import json
import os
import re
import urllib.request
import urllib.error
from typing import Dict, List, Optional
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def is_gemini_available() -> bool:
    """Check if Gemini API key is configured."""
    return bool(GEMINI_API_KEY and len(GEMINI_API_KEY) > 10)


def call_gemini_api(prompt: str, system_instruction: str = "", temperature: float = 0.3) -> Optional[str]:
    """Call Google Gemini REST API directly."""
    if not is_gemini_available():
        return None

    url = f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json"
        }
    }

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            candidates = resp_data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
    except Exception as exc:
        print(f"Gemini API request notice: {repr(exc)}. Using built-in intelligent fallback.")
        return None
    return None


def analyze_resume_with_ai(resume_text: str, target_role: str, candidate_skills: List[str]) -> dict:
    """Analyze resume with Gemini AI or apply rich structured fallback."""
    if is_gemini_available():
        prompt = f"""
You are an expert technical recruiter and career coach.
Analyze the following resume for the target role: "{target_role}".
Known extracted skills: {candidate_skills}

Resume excerpt:
{resume_text[:2500]}

Return JSON with this exact schema:
{{
    "professional_summary": "2-3 sentences summarizing background and career trajectory",
    "experience_level": "Entry-Level | Intermediate | Senior",
    "detected_strengths": ["string", "string", "string"],
    "key_achievements": ["string", "string"],
    "coaching_advice": "Actionable advice to become fully job-ready for {target_role}"
}}
"""
        response_text = call_gemini_api(prompt, system_instruction="Respond with valid JSON only.")
        if response_text:
            try:
                # Clean possible markdown fence blocks
                cleaned = re.sub(r"^```json\s*|\s*```$", "", response_text.strip(), flags=re.MULTILINE)
                return json.loads(cleaned)
            except Exception:
                pass

    # High-quality fallback heuristics
    exp_level = "Entry-Level"
    if len(candidate_skills) >= 8:
        exp_level = "Intermediate"
    elif len(candidate_skills) >= 12:
        exp_level = "Experienced"

    strengths = []
    if "python" in candidate_skills:
        strengths.append("Demonstrated Python scripting & core programming capabilities")
    if "sql" in candidate_skills:
        strengths.append("Proficiency with relational database querying & data retrieval")
    if any(s in candidate_skills for s in ["react", "html", "javascript"]):
        strengths.append("Practical experience building responsive web interfaces")
    if "git" in candidate_skills:
        strengths.append("Familiarity with version control workflows and collaborative development")
    if not strengths:
        strengths = ["Strong analytical problem-solving foundation", "Motivated technical aptitude"]

    return {
        "professional_summary": f"Candidate demonstrates foundational competencies suitable for {target_role}. Shows technical aptitude across {len(candidate_skills)} recognized domain skills and practical coding foundations.",
        "experience_level": exp_level,
        "detected_strengths": strengths,
        "key_achievements": [
            f"Successfully built projects using {', '.join(candidate_skills[:3]) if candidate_skills else 'core programming tools'}",
            "Applied consistent technical problem solving across academic and practical coursework"
        ],
        "coaching_advice": f"Focus on closing identified high-impact skill gaps for {target_role}, complete real-world portfolio capstones, and test technical mastery through targeted weekly assessments."
    }


def generate_ai_adaptive_recommendation(skill: str, score: float, week: int) -> dict:
    """Generate adaptive plan advice for a weekly test score."""
    if score >= 80:
        level = "Advanced Acceleration"
        advice = f"Outstanding performance on {skill.title()} ({score:.0f}%). Proceed immediately to advanced topics, production optimization, and complex portfolio integration."
    elif score >= 50:
        level = "Targeted Practice"
        advice = f"Solid foundational grasp of {skill.title()} ({score:.0f}%). Allocate additional practice hours to edge cases, debugging scenarios, and practical project deliverables."
    else:
        level = "Comprehensive Reinforcement"
        advice = f"Needs reinforcement in {skill.title()} ({score:.0f}%). We have injected guided revision modules, fundamental concept reviews, and step-by-step code exercises before moving forward."

    return {
        "skill": skill,
        "week": week,
        "score_percent": score,
        "mastery_tier": level,
        "recommendation_summary": advice
    }
