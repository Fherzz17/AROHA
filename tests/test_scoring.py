"""
Unit tests for SkillPulse Score calculation and market intelligence
Team: Syntax Society
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.scoring import calculate_skillpulse_score
from services.market_intelligence import (
    get_salary_vs_experience,
    get_top_hiring_companies,
    get_skill_salary_associations
)
from services.recommender import generate_personalized_recommendations

def test_skillpulse_score_components():
    res = calculate_skillpulse_score("Python")
    assert "skillpulse_score" in res
    assert 20 <= res["skillpulse_score"] <= 100
    comp = res["components"]
    assert "demand" in comp
    assert "role_coverage" in comp
    assert "salary_signal" in comp
    assert "emerging_signal" in comp
    assert res["empirical_metrics"]["observed_postings"] > 0

def test_market_intelligence_services():
    sal_exp = get_salary_vs_experience()
    assert len(sal_exp) > 0
    assert "avg_salary_lpa" in sal_exp[0]

    top_comp = get_top_hiring_companies(limit=10)
    assert len(top_comp) > 0
    assert "total_openings" in top_comp[0]

    assoc = get_skill_salary_associations()
    assert len(assoc) > 0
    assert "associated_avg_salary_lpa" in assoc[0]

def test_enhanced_recommendations():
    rec = generate_personalized_recommendations("Data Scientist", ["Python", "SQL"])
    assert rec["target_role"] == "Data Scientist"
    assert len(rec["top_recommendations"]) > 0
    first = rec["top_recommendations"][0]
    assert "skill" in first
    assert "priority_score" in first
    assert "why_recommended" in first

def test_daily_emerging_skills_engine():
    from datetime import date, timedelta
    from services.emerging_service import emerging_service

    today = date.today()
    tomorrow = today + timedelta(days=1)

    catalog_today = emerging_service.get_catalog_with_daily_metrics(today)
    assert len(catalog_today) >= 8
    genai_today = next(item for item in catalog_today if item["skill_name"] == "Generative AI")

    assert "daily_delta_pct" in genai_today
    assert "trend_direction" in genai_today
    assert "history_7d" in genai_today
    assert len(genai_today["history_7d"]) == 7
    assert 50 <= genai_today["signal_strength"] <= 99

    catalog_tomorrow = emerging_service.get_catalog_with_daily_metrics(tomorrow)
    genai_tomorrow = next(item for item in catalog_tomorrow if item["skill_name"] == "Generative AI")
    assert genai_tomorrow["as_of_date"] == tomorrow.isoformat()
