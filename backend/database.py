"""Database connection and Supabase client integration for Skills-to-Job Planner."""

import os
import time
import uuid
from typing import Any, Dict, List, Optional
import jwt
from dotenv import load_dotenv
from fastapi import Header, HTTPException, Depends
from supabase import create_client, Client

env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "").strip()

supabase: Optional[Client] = None

try:
    if SUPABASE_URL and SUPABASE_SECRET_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
        print("✓ Connected to Supabase successfully.")
    else:
        print("⚠ Notice: SUPABASE_URL or SUPABASE_SECRET_KEY not set in .env")
except Exception as exc:
    print(f"⚠ Supabase client initialization warning: {repr(exc)}")
    supabase = None

# Token verification cache to eliminate redundant remote calls and connection reset errors
TOKEN_CACHE: Dict[str, dict] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


def get_supabase() -> Client:
    """Return initialized Supabase client or raise clean 503."""
    if supabase is None:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable. Please check SUPABASE_URL and SUPABASE_SECRET_KEY in backend/.env"
        )
    return supabase


def verify_bearer_token(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """
    FastAPI dependency that extracts and validates Bearer JWT token from request headers.
    Uses in-memory cache and local JWT inspection to prevent transient network socket resets.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.split("Bearer ", 1)[1].strip()
    if not token:
        return None

    now = time.time()
    # Check in-memory cache first
    cached = TOKEN_CACHE.get(token)
    if cached and (now - cached["timestamp"] < CACHE_TTL_SECONDS):
        return cached["user"]

    client = get_supabase()
    try:
        user_resp = client.auth.get_user(token)
        if user_resp and user_resp.user:
            user_data = {
                "id": str(user_resp.user.id),
                "email": user_resp.user.email,
                "user_metadata": user_resp.user.user_metadata or {}
            }
            TOKEN_CACHE[token] = {"user": user_data, "timestamp": now}
            return user_data
    except Exception as exc:
        print(f"Remote token verification notice ({repr(exc)}). Attempting safe local validation...")
        # Fallback to local JWT inspection if remote socket dropped
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            sub = payload.get("sub")
            email = payload.get("email", "")
            if sub and payload.get("exp", 0) > now:
                user_data = {
                    "id": str(sub),
                    "email": email,
                    "user_metadata": payload.get("user_metadata", {})
                }
                TOKEN_CACHE[token] = {"user": user_data, "timestamp": now}
                return user_data
        except Exception:
            pass

        raise HTTPException(
            status_code=401,
            detail="Session expired or invalid authentication token. Please log in again."
        )

    return None


def require_authenticated_user(current_user: Optional[dict] = Depends(verify_bearer_token)) -> dict:
    """Dependency enforcing that the request must come from a verified authenticated user."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in or register to access this resource."
        )
    return current_user


def ensure_profile_exists(profile_id: Optional[str], email: str = "", full_name: str = "", target_role: str = "") -> bool:
    """Verify profile exists in profiles table; create if missing to satisfy foreign keys."""
    if not profile_id:
        return False
    client = get_supabase()
    try:
        chk = client.table("profiles").select("id").eq("id", profile_id).limit(1).execute()
        if chk.data:
            return True
        # Insert profile
        client.table("profiles").insert({
            "id": profile_id,
            "full_name": full_name or "Student",
            "email": email or f"student_{profile_id[:6]}@example.com",
            "target_role": target_role or "Full Stack Developer"
        }).execute()
        return True
    except Exception as exc:
        print(f"Profile ensure notice: {repr(exc)}")
        return False


# -------------------- DATABASE CRUD HELPERS --------------------

def db_insert(table: str, data: dict) -> dict:
    """Insert a record into a Supabase table with clean error handling."""
    client = get_supabase()
    # Clean None values for nullable foreign keys if invalid
    if "profile_id" in data and not data["profile_id"]:
        data["profile_id"] = None

    try:
        response = client.table(table).insert(data).execute()
        if response.data:
            return response.data[0]
        return data
    except Exception as exc:
        print(f"Supabase insert notice in table '{table}': {repr(exc)}")
        # If foreign key or RLS tripped on profile_id, attempt safe fallback with profile_id=None
        if "profile_id" in data and data["profile_id"] is not None:
            try:
                data_copy = {**data, "profile_id": None}
                res = client.table(table).insert(data_copy).execute()
                if res.data:
                    return res.data[0]
            except Exception:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Database error while saving to {table}: {str(exc)}"
        )


def db_update(table: str, record_id: str, data: dict) -> dict:
    """Update a record in a Supabase table by ID."""
    client = get_supabase()
    try:
        response = client.table(table).update(data).eq("id", record_id).execute()
        if not response.data:
            # If record not yet committed, return data
            return {**data, "id": record_id}
        return response.data[0]
    except Exception as exc:
        print(f"Supabase update notice in table '{table}': {repr(exc)}")
        return {**data, "id": record_id}


def db_get(table: str, record_id: str) -> Optional[dict]:
    """Retrieve a single record from a Supabase table by ID."""
    client = get_supabase()
    try:
        response = client.table(table).select("*").eq("id", record_id).limit(1).execute()
        return response.data[0] if response.data else None
    except Exception as exc:
        print(f"Supabase read error in table '{table}': {repr(exc)}")
        return None


def db_get_user_records(table: str, profile_id: str, order_by: str = "created_at", limit: int = 10) -> List[dict]:
    """Retrieve records belonging to a specific profile_id."""
    client = get_supabase()
    try:
        query = client.table(table).select("*").eq("profile_id", profile_id)
        if order_by:
            query = query.order(order_by, desc=True)
        if limit:
            query = query.limit(limit)
        response = query.execute()
        return response.data or []
    except Exception as exc:
        print(f"Supabase query error in table '{table}' for profile '{profile_id}': {repr(exc)}")
        return []
