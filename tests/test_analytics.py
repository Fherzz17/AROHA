"""
Unit tests for Database, Analytics Service, and Trend Forecasting
Team: Syntax Society
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend import database
from services import analytics_service
from services.trend_forecaster import forecast_skill_trend

def test_database_counts():
    total_jobs = database.get_total_jobs_count()
    assert total_jobs > 1000, f"Expected >1000 jobs in seeded DB, found {total_jobs}"

    skills = database.get_all_skills_list()
    assert len(skills) >= 20, f"Expected >=20 unique skills, found {len(skills)}"
    assert "Python" in skills
    assert "SQL" in skills

def test_dashboard_summary():
    summary = analytics_service.get_dashboard_summary()
    assert summary["total_jobs_analyzed"] > 1000
    assert len(summary["top_skills"]) > 0
    assert len(summary["fastest_growing_skills"]) > 0

def test_skill_profile():
    profile = analytics_service.get_skill_profile("Python")
    assert profile is not None
    assert profile["skill_name"] == "Python"
    assert profile["demand_score"] > 0
    assert len(profile["historical_trend"]) > 0
    assert len(profile["forecast_trend"]) > 0
    assert len(profile["related_skills"]) > 0

def test_observed_vs_forecast_separation():
    quarterly_data = [
        {"quarter": "2024-Q1", "count": 100},
        {"quarter": "2024-Q2", "count": 120},
        {"quarter": "2024-Q3", "count": 145},
        {"quarter": "2024-Q4", "count": 170},
        {"quarter": "2025-Q1", "count": 210}
    ]
    res = forecast_skill_trend("Generative AI", quarterly_data)

    # Historical points must be marked is_forecast=False
    for p in res.historical_points:
        assert p.is_forecast is False

    # Forecast points must be marked is_forecast=True and have confidence bounds
    for p in res.forecast_points:
        assert p.is_forecast is True
        assert p.confidence_low is not None
        assert p.confidence_high is not None
        assert p.confidence_low <= p.count <= p.confidence_high
