"""
Unit tests for Personalized Skill Gap and Recommendation Service
Team: Syntax Society
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.recommender_service import recommend_skills

def test_data_analyst_recommendation_flow():
    """
    User scenario:
    Target Role: Data Analyst
    User Current Skills: SQL, Excel
    Expected:
    - Identifies missing core skills like Python, Power BI
    - Recommends next skills with roadmap steps
    - Returns match score
    """
    res = recommend_skills("Data Analyst", ["SQL", "Excel"])

    assert res["target_role"] == "Data Analyst"
    assert "SQL" in res["matched_skills"] or "SQL" in res["skill_gap_summary"]["core_completed"]
    assert len(res["missing_core_skills"]) > 0
    assert "Power BI" in res["missing_core_skills"] or "Python" in res["missing_core_skills"]

    assert len(res["recommended_next_skills"]) > 0
    assert len(res["learning_roadmap"]) > 0

    # Check roadmap step structure
    first_step = res["learning_roadmap"][0]
    assert "step_number" in first_step
    assert "skill" in first_step
    assert "why_needed" in first_step
    assert len(first_step["recommended_resources"]) > 0

def test_perfect_match_case():
    all_core = ["Python", "SQL", "Power BI", "Tableau", "Data Analysis", "Pandas"]
    res = recommend_skills("Data Analyst", all_core)

    assert res["match_percentage"] >= 60.0
    assert len(res["missing_core_skills"]) == 0
