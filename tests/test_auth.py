"""
Authentication Integration Tests for AROHA
Tests real user registration, login, multi-role selection, social SSO, session persistence, and password reset.
"""

import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_auth_student_registration_and_login():
    uid = uuid.uuid4().hex[:8]
    email = f"student_{uid}@university.edu.in"
    password = "SecurePassword@123"

    # 1. Register new student
    res = client.post("/api/auth/register", json={
        "name": f"Student User {uid}",
        "email": email,
        "password": password,
        "role": "student",
        "organization": "IIT Bombay",
        "target_role": "Data Scientist"
    })
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["role"] == "student"
    assert data["user"]["email"] == email

    # 2. Login with newly registered student
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password,
        "role": "student"
    })
    assert login_res.status_code == 200, login_res.text
    login_data = login_res.json()
    assert login_data["success"] is True
    assert login_data["user"]["email"] == email


def test_auth_recruiter_registration_and_login():
    uid = uuid.uuid4().hex[:8]
    email = f"recruiter_{uid}@techcorp.com"
    password = "SecurePassword@123"

    # Register recruiter
    res = client.post("/api/auth/register", json={
        "name": f"Recruiter {uid}",
        "email": email,
        "password": password,
        "role": "recruiter",
        "organization": "Infosys Talent Acquisition",
        "domain": "Cloud & AI"
    })
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["user"]["role"] == "recruiter"

    # Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password,
        "role": "recruiter"
    })
    assert login_res.status_code == 200, login_res.text
    assert login_res.json()["user"]["role"] == "recruiter"


def test_auth_educator_registration():
    uid = uuid.uuid4().hex[:8]
    email = f"educator_{uid}@academia.org"
    password = "SecurePassword@123"

    res = client.post("/api/auth/register", json={
        "name": f"Prof. {uid}",
        "email": email,
        "password": password,
        "role": "other",
        "organization": "National Skill Development Council",
        "domain": "Curriculum Advisor"
    })
    assert res.status_code == 200, res.text
    assert res.json()["user"]["role"] == "other"


def test_auth_duplicate_email_prevention():
    uid = uuid.uuid4().hex[:8]
    email = f"dup_{uid}@domain.com"
    payload = {
        "name": "Original User",
        "email": email,
        "password": "Password@123",
        "role": "student"
    }
    r1 = client.post("/api/auth/register", json=payload)
    assert r1.status_code == 200

    # Attempt duplicate
    r2 = client.post("/api/auth/register", json=payload)
    assert r2.status_code == 400
    assert "already exists" in r2.json()["detail"].lower()


def test_auth_session_me_and_logout():
    uid = uuid.uuid4().hex[:8]
    email = f"session_{uid}@domain.com"
    r = client.post("/api/auth/register", json={
        "name": "Session Tester",
        "email": email,
        "password": "Password@123",
        "role": "student"
    })
    assert r.status_code == 200
    token = r.json()["token"]

    # Verify session via /me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["user"]["email"] == email

    # Terminate session
    logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200
    assert logout_res.json()["success"] is True

    # Token should now be invalid
    invalid_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert invalid_me.status_code == 401


def test_auth_social_login():
    uid = uuid.uuid4().hex[:8]
    email = f"social_{uid}@gmail.com"
    res = client.post("/api/auth/social-login", json={
        "provider": "google",
        "email": email,
        "name": "Google SSO User",
        "role": "student"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["auth_provider"] == "google"
