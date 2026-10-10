"""
API Endpoint Integration Tests for SkillPulse Bharat
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

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["team"] == "Syntax Society"
    assert data["database_records"] > 0

def test_api_dashboard():
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "total_jobs_analyzed" in data
    assert "top_skills" in data
    assert len(data["top_skills"]) > 0

def test_api_skill_detail():
    res = client.get("/api/skills/Python")
    assert res.status_code == 200
    data = res.json()
    assert data["skill_name"] == "Python"
    assert "historical_trend" in data
    assert "forecast_trend" in data

def test_api_role_detail():
    res = client.get("/api/roles/Data%20Scientist")
    assert res.status_code == 200
    data = res.json()
    assert data["role_name"] == "Data Scientist"
    assert len(data["core_skills"]) > 0

def test_api_emerging():
    res = client.get("/api/emerging")
    assert res.status_code == 200
    data = res.json()
    assert "skills" in data
    assert len(data["skills"]) > 0
    assert "disclaimer" in data

def test_api_recommend():
    res = client.post("/api/recommend", json={
        "target_role": "Python Developer",
        "user_skills": ["Python", "Git"],
        "experience_level": "Fresher"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["target_role"] == "Python Developer"
    assert "match_percentage" in data
    assert len(data["learning_roadmap"]) > 0

def test_api_extract():
    res = client.post("/api/extract", json={
        "text": "Looking for a Python developer with experience in SQL, AWS, Docker and Machine Learning."
    })
    assert res.status_code == 200
    data = res.json()
    skills = data["extracted_skills"]
    assert "Python" in skills
    assert "SQL" in skills
    assert "AWS" in skills
    assert "Docker" in skills
    assert "Machine Learning" in skills
    assert len(data["top_matching_roles"]) > 0
