"""
Unit & Integration Tests for AI Resume Job Matcher
Team: Syntax Society
"""

import sys
from pathlib import Path
from io import BytesIO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.app import app
from services.job_matching import job_matcher, generate_job_links, estimate_experience_from_text

client = TestClient(app)

SAMPLE_RESUME_TEXT = """
Jane Doe
Senior Data Scientist
Email: jane.doe@example.com | Bengaluru, India
Experience: 5+ years of hands-on experience in Machine Learning and Data Science.

Technical Skills:
- Programming: Python, SQL, R
- Machine Learning: Scikit-learn, TensorFlow, Deep Learning, Pandas, NumPy
- Cloud & MLOps: AWS, Docker, Git
- Analytics: Statistics, Data Analysis

Work Experience:
Lead Data Scientist at Tech Analytics (2020 - 2024):
- Built production recommendation engines and predictive churn models in Python and TensorFlow.
- Deployed ML pipelines on AWS using Docker.
"""

def test_experience_estimation():
    exp_years, tier = estimate_experience_from_text(SAMPLE_RESUME_TEXT)
    assert exp_years >= 4
    assert "Mid-Level" in tier or "Senior" in tier

    fresher_text = "Recent B.Tech graduate looking for an internship or fresher software engineering role."
    f_years, f_tier = estimate_experience_from_text(fresher_text)
    assert f_years <= 1
    assert "Fresher" in f_tier

def test_job_links_generation():
    links = generate_job_links("Data Scientist", "Tata Consultancy Services", "Bengaluru, Karnataka")
    assert "linkedin.com/jobs/search" in links["apply_url"]
    assert "linkedin.com" in links["linkedin_url"]
    assert "naukri.com" in links["naukri_url"]
    assert "google.com/search" in links["google_jobs_url"]
    assert "indeed.com" in links["indeed_url"]
    assert "careers" in links["company_careers_url"]
    assert "Data%20Scientist" in links["apply_url"]

def test_resume_matching_scoring_and_ranking():
    result = job_matcher.match_resume(
        resume_text=SAMPLE_RESUME_TEXT,
        min_score=30.0,
        limit=10
    )
    assert "candidate_profile" in result
    cand_profile = result["candidate_profile"]
    assert "Python" in cand_profile["extracted_skills"]
    assert "SQL" in cand_profile["extracted_skills"]
    assert "Machine Learning" in cand_profile["extracted_skills"]
    assert result["total_jobs_searched"] > 0
    assert result["matched_count"] > 0
    assert len(result["jobs"]) > 0

    top_job = result["jobs"][0]
    assert "job_title" in top_job
    assert "company" in top_job
    assert "match_score" in top_job
    assert top_job["match_score"] >= 60.0
    assert "matched_skills" in top_job
    assert len(top_job["matched_skills"]) > 0
    assert "links" in top_job
    assert "apply_url" in top_job["links"]
    assert top_job["links"]["apply_url"].startswith("http")

def test_role_and_location_filters():
    result = job_matcher.match_resume(
        resume_text=SAMPLE_RESUME_TEXT,
        target_role="Data Scientist",
        location_filter="Bengaluru",
        min_score=20.0,
        limit=5
    )
    for job in result["jobs"]:
        assert "data scientist" in job["job_title"].lower()
        assert "bengaluru" in job["location"].lower()

def test_api_jobs_match_json_endpoint():
    res = client.post("/api/jobs/match", json={
        "resume_text": SAMPLE_RESUME_TEXT,
        "min_score": 30.0,
        "limit": 5
    })
    assert res.status_code == 200
    data = res.json()
    assert "candidate_profile" in data
    assert len(data["jobs"]) > 0
    first_job = data["jobs"][0]
    assert "apply_url" in first_job["links"]
    assert first_job["match_score"] > 0

def test_api_jobs_match_resume_upload_endpoint():
    file_bytes = SAMPLE_RESUME_TEXT.encode("utf-8")
    files = {"file": ("resume.txt", file_bytes, "text/plain")}
    res = client.post("/api/jobs/match-resume", files=files)
    assert res.status_code == 200
    data = res.json()
    assert "candidate_profile" in data
    assert data["matched_count"] > 0
    assert len(data["jobs"]) > 0
    assert "apply_url" in data["jobs"][0]["links"]

def test_api_jobs_locations_and_single_job():
    loc_res = client.get("/api/jobs/locations")
    assert loc_res.status_code == 200
    loc_data = loc_res.json()
    assert len(loc_data["locations"]) > 0

    single_res = client.get("/api/jobs/1")
    assert single_res.status_code == 200
    single_job = single_res.json()
    assert single_job["id"] == 1
    assert "links" in single_job
    assert "apply_url" in single_job["links"]
