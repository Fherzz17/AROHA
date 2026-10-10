"""
Authentication and User Management Module for SkillPulse Bharat
Supports multi-role logins (Student, Recruiter, Other/Educator),
email/password auth, social login simulations, and demo fast-logins.
Team: Syntax Society
"""

import os
import hashlib
import hmac
import secrets
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr, Field

# Market data is shipped read-only. On Vercel, the deployed filesystem is
# read-only, so authentication uses a per-instance copy in /tmp. This keeps
# the demo login functional while making the serverless storage limitation
# explicit; a production deployment should use a managed database instead.
PROJECT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "job_market.db"
if os.getenv("VERCEL"):
    DB_PATH = Path("/tmp") / "aroha_auth.db"
    if not DB_PATH.exists():
        shutil.copy2(PROJECT_DB_PATH, DB_PATH)
else:
    DB_PATH = PROJECT_DB_PATH

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


# ----------------- Database Setup & Helpers ----------------- #

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a random salt."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt.hex() + "$" + key.hex()


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a plain password against the stored salt$key hash."""
    try:
        salt_hex, key_hex = stored_hash.split("$")
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return hmac.compare_digest(key, expected_key)
    except Exception:
        return False


def init_auth_db():
    """Initializes user and session tables, and pre-seeds demo accounts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                role TEXT NOT NULL CHECK(role IN ('student', 'recruiter', 'other')),
                organization TEXT,
                target_role TEXT,
                domain TEXT,
                auth_provider TEXT DEFAULT 'local',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        conn.commit()

        # Seed Demo Accounts if not present
        demo_accounts = [
            {
                "name": "Aarav Sharma",
                "email": "student@skillpulse.in",
                "password": "Password@123",
                "role": "student",
                "organization": "IIT Bombay",
                "target_role": "Data Scientist",
                "domain": "AI / Data Science"
            },
            {
                "name": "Priya Patel",
                "email": "recruiter@techhire.in",
                "password": "Password@123",
                "role": "recruiter",
                "organization": "Zomato Talent Acquisition",
                "target_role": "Tech Recruiter",
                "domain": "Cloud & AI Talent"
            },
            {
                "name": "Dr. Ramesh Verma",
                "email": "educator@academia.in",
                "password": "Password@123",
                "role": "other",
                "organization": "National Skill Development Council (NSDC)",
                "target_role": "Curriculum Advisor",
                "domain": "EdTech & Skills Policy"
            }
        ]

        for acc in demo_accounts:
            cursor.execute("SELECT id FROM users WHERE lower(email) = lower(?)", (acc["email"],))
            if not cursor.fetchone():
                pw_hash = hash_password(acc["password"])
                cursor.execute("""
                    INSERT INTO users (name, email, password_hash, role, organization, target_role, domain, auth_provider)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'local')
                """, (
                    acc["name"],
                    acc["email"].lower(),
                    pw_hash,
                    acc["role"],
                    acc["organization"],
                    acc["target_role"],
                    acc["domain"]
                ))
        conn.commit()


# Initialize database schema on module import
init_auth_db()


# ----------------- Pydantic Schemas ----------------- #

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field("student", pattern="^(student|recruiter|other)$")
    organization: Optional[str] = None
    target_role: Optional[str] = None
    domain: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = None  # Optional check for role


class SocialLoginRequest(BaseModel):
    provider: str = Field(..., pattern="^(google|linkedin|github|microsoft)$")
    email: str
    name: str
    role: str = Field("student", pattern="^(student|recruiter|other)$")
    organization: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str = Field(..., min_length=6)


class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    role: str
    organization: Optional[str] = None
    target_role: Optional[str] = None
    domain: Optional[str] = None
    auth_provider: str
    token: Optional[str] = None


# ----------------- Session Utilities ----------------- #

def create_session(user_id: int) -> str:
    token = secrets.token_hex(32)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
        cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        conn.commit()
    return token


def get_user_by_token(token: str) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.name, u.email, u.role, u.organization, u.target_role, u.domain, u.auth_provider, u.last_login
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ?
        """, (token,))
        row = cursor.fetchone()
        return dict(row) if row else None


# ----------------- Auth Endpoints ----------------- #

@auth_router.post("/register")
async def register(payload: RegisterRequest):
    """Registers a new user account with role-specific profile metadata."""
    email_clean = payload.email.strip().lower()
    if "@" not in email_clean or "." not in email_clean:
        raise HTTPException(status_code=400, detail="Please provide a valid email address.")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE lower(email) = ?", (email_clean,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="An account with this email address already exists. Please sign in.")

        pw_hash = hash_password(payload.password)
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, organization, target_role, domain, auth_provider)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'local')
        """, (
            payload.name.strip(),
            email_clean,
            pw_hash,
            payload.role.lower(),
            payload.organization.strip() if payload.organization else None,
            payload.target_role.strip() if payload.target_role else None,
            payload.domain.strip() if payload.domain else None
        ))
        conn.commit()
        user_id = cursor.lastrowid

    token = create_session(user_id)
    return {
        "success": True,
        "message": f"Welcome to SkillPulse Bharat, {payload.name}!",
        "token": token,
        "user": {
            "id": user_id,
            "name": payload.name,
            "email": email_clean,
            "role": payload.role,
            "organization": payload.organization,
            "target_role": payload.target_role,
            "domain": payload.domain,
            "auth_provider": "local"
        }
    }


@auth_router.post("/login")
async def login(payload: LoginRequest):
    """Authenticates existing user with email and password."""
    email_clean = payload.email.strip().lower()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, email, password_hash, role, organization, target_role, domain, auth_provider
            FROM users
            WHERE lower(email) = ?
        """, (email_clean,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="No account found with this email. Please check your spelling or sign up.")

        user_dict = dict(user)
        if not verify_password(payload.password, user_dict["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect password. Please verify your credentials.")

        # If user explicitly selected a role tab, verify or update
        if payload.role and payload.role.lower() != user_dict["role"].lower():
            # Allow flexible login across roles or notify
            pass

    token = create_session(user_dict["id"])
    del user_dict["password_hash"]
    user_dict["token"] = token

    return {
        "success": True,
        "message": f"Welcome back, {user_dict['name']}!",
        "token": token,
        "user": user_dict
    }


@auth_router.post("/social-login")
async def social_login(payload: SocialLoginRequest):
    """
    Handles single-sign-on (Google, LinkedIn, GitHub, Microsoft).
    If user doesn't exist, automatically registers with selected role.
    """
    email_clean = payload.email.strip().lower()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, email, role, organization, target_role, domain, auth_provider
            FROM users WHERE lower(email) = ?
        """, (email_clean,))
        existing = cursor.fetchone()

        if existing:
            user_dict = dict(existing)
            user_id = user_dict["id"]
        else:
            # Create user for social login
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role, organization, target_role, domain, auth_provider)
                VALUES (?, ?, NULL, ?, ?, ?, NULL, ?)
            """, (
                payload.name,
                email_clean,
                payload.role,
                payload.organization or ("Tech University" if payload.role == "student" else "Independent"),
                "Full Stack Developer" if payload.role == "student" else None,
                payload.provider
            ))
            conn.commit()
            user_id = cursor.lastrowid
            cursor.execute("SELECT id, name, email, role, organization, target_role, domain, auth_provider FROM users WHERE id = ?", (user_id,))
            user_dict = dict(cursor.fetchone())

    token = create_session(user_id)
    user_dict["token"] = token

    return {
        "success": True,
        "message": f"Authenticated via {payload.provider.title()}.",
        "token": token,
        "user": user_dict
    }


@auth_router.get("/me")
async def get_current_user_profile(authorization: Optional[str] = Header(None)):
    """Returns profile for currently active session token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authentication token provided.")

    token = authorization.replace("Bearer ", "").strip()
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid. Please sign in again.")

    return {"user": user}


@auth_router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Terminates active session."""
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()
    return {"success": True, "message": "Successfully logged out."}


@auth_router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest):
    """Simulates password reset for forgot-password workflows."""
    email_clean = payload.email.strip().lower()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE lower(email) = ?", (email_clean,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="No registered account found with this email.")

        new_hash = hash_password(payload.new_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE lower(email) = ?", (new_hash, email_clean))
        conn.commit()

    return {"success": True, "message": "Password successfully updated! You can now log in with your new password."}


@auth_router.get("/demo-accounts")
async def get_demo_accounts():
    """Returns demo credentials for 1-click evaluation."""
    return {
        "student": {
            "role": "student",
            "name": "Aarav Sharma (Student)",
            "email": "student@skillpulse.in",
            "password": "Password@123",
            "organization": "IIT Bombay",
            "target_role": "Data Scientist"
        },
        "recruiter": {
            "role": "recruiter",
            "name": "Priya Patel (Recruiter)",
            "email": "recruiter@techhire.in",
            "password": "Password@123",
            "organization": "Zomato Talent Acquisition",
            "domain": "Cloud & AI Talent"
        },
        "other": {
            "role": "other",
            "name": "Dr. Ramesh Verma (Educator / Policy)",
            "email": "educator@academia.in",
            "password": "Password@123",
            "organization": "National Skill Development Council (NSDC)",
            "domain": "EdTech & Skills Policy"
        }
    }
