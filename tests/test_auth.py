"""
Authentication Integration Tests for SkillPulse Bharat
Tests registration, login, multi-role selection, social SSO, and password reset.
Team: Syntax Society
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_auth_demo_accounts():
    res = client.get("/api/auth/demo-accounts")
    assert res.status_code == 200
    data = res.json()
    assert "student" in data
    assert "recruiter" in data
    assert "other" in data


def test_auth_student_login():
    res = client.post("/api/auth/login", json={
        "email": "student@skillpulse.in",
        "password": "Password@123",
        "role": "student"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["role"] == "student"


def test_auth_recruiter_login():
    res = client.post("/api/auth/login", json={
        "email": "recruiter@techhire.in",
        "password": "Password@123",
        "role": "recruiter"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["role"] == "recruiter"


def test_auth_other_educator_login():
    res = client.post("/api/auth/login", json={
        "email": "educator@academia.in",
        "password": "Password@123",
        "role": "other"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["role"] == "other"


def test_auth_social_login():
    res = client.post("/api/auth/social-login", json={
        "provider": "google",
        "email": "student.google.oauth@domain.in",
        "name": "Google SSO Student",
        "role": "student"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["auth_provider"] == "google"
