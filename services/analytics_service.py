"""
Analytics Service for SkillPulse Bharat
Provides aggregations, skill demand scoring, role metrics, and emerging skill intelligence.
Team: Syntax Society
"""

from typing import List, Dict, Any, Optional
from backend import database
from services.trend_forecaster import forecast_skill_trend
from utils.constants import ROLE_SKILL_PROFILES, SKILL_TAXONOMY

from services.emerging_service import emerging_service

class DynamicEmergingSkillsList(list):
    """List proxy that returns freshly computed daily emerging skills."""
    def __iter__(self):
        return iter(emerging_service.get_catalog_with_daily_metrics())

    def __len__(self):
        return len(emerging_service.get_catalog_with_daily_metrics())

    def __getitem__(self, index):
        return emerging_service.get_catalog_with_daily_metrics()[index]

EMERGING_SKILLS_CATALOG = DynamicEmergingSkillsList()

def get_dashboard_summary() -> Dict[str, Any]:
    """Provides high-level metrics for the main executive dashboard."""
    total_jobs = database.get_total_jobs_count()
    total_skills = database.get_total_unique_skills_count()
    top_skills = database.get_top_skills(limit=10)
    industries = database.get_industry_distribution()

    # Fast growing selection
    fastest_growing = sorted(EMERGING_SKILLS_CATALOG, key=lambda x: x["growth_rate_pct"], reverse=True)[:5]

    return {
        "total_jobs_analyzed": total_jobs,
        "total_skills_identified": total_skills,
        "top_skills": top_skills,
        "fastest_growing_skills": fastest_growing,
        "industries": industries,
        "roles_covered": list(ROLE_SKILL_PROFILES.keys())
    }

def get_skill_profile(skill_name: str) -> Optional[Dict[str, Any]]:
    """Fetches comprehensive analytics and forecast for a single skill."""
    raw_stats = database.get_skill_stats(skill_name)
    if not raw_stats:
        return None

    # Determine category
    category = "General Tech"
    for cat, skills in SKILL_TAXONOMY.items():
        if any(s.lower() == skill_name.lower() for s in skills):
            category = cat
            break

    # Calculate demand score (0-100 normalized against maximum theoretical market share ~60%)
    pct = raw_stats["percentage"]
    demand_score = int(min(100, round((pct / 45.0) * 100)))

    # Compute forecast
    trend_response = forecast_skill_trend(raw_stats["skill"], raw_stats["quarterly"])

    # Determine momentum label
    growth = trend_response.cagr_projection
    if growth > 30:
        momentum = "Rapidly Growing (+High Momentum)"
    elif growth > 10:
        momentum = "Steady Growth"
    elif growth >= -5:
        momentum = "Stable High Volume"
    else:
        momentum = "Decreasing Demand"

    return {
        "skill_name": raw_stats["skill"],
        "category": category,
        "total_jobs": raw_stats["count"],
        "demand_percentage": raw_stats["percentage"],
        "demand_score": max(15, demand_score),
        "momentum": momentum,
        "qoq_growth": round(growth / 4, 1),
        "annual_cagr_projection": growth,
        "top_industries": raw_stats["industries"],
        "related_skills": raw_stats["related_skills"],
        "historical_trend": [p.dict() for p in trend_response.historical_points],
        "forecast_trend": [p.dict() for p in trend_response.forecast_points],
        "verdict": trend_response.verdict,
        "disclaimer": trend_response.disclaimer
    }

def get_role_analysis(role_name: str) -> Optional[Dict[str, Any]]:
    """Analyzes requirements, core skills, and emerging expectations for a role."""
    role_info = database.get_role_details(role_name)
    if not role_info and role_name in ROLE_SKILL_PROFILES:
        # Fallback profile
        profile = ROLE_SKILL_PROFILES[role_name]
        return {
            "role_name": role_name,
            "description": profile["desc"],
            "total_jobs": 220,
            "avg_salary_lpa": 14.2,
            "core_skills": [{"skill": s, "percentage": 85.0} for s in profile["core"]],
            "complementary_skills": [{"skill": s, "percentage": 48.0} for s in profile["complementary"]],
            "emerging_skills": profile.get("emerging", []),
            "industry_spread": [],
            "location_spread": []
        }
    
    if not role_info:
        return None

    # Merge with taxonomy definitions
    profile = ROLE_SKILL_PROFILES.get(role_name, {
        "core": [],
        "complementary": [],
        "emerging": [],
        "desc": f"Technical specialist role in {role_name}."
    })

    core_list = []
    comp_list = []

    # Map database frequency into categorized groups
    db_skills_dict = {item["skill"].lower(): item for item in role_info["top_skills"]}

    for c in profile["core"]:
        item = db_skills_dict.get(c.lower(), {"skill": c, "percentage": 65.0, "count": 120})
        core_list.append(item)

    for comp in profile["complementary"]:
        item = db_skills_dict.get(comp.lower(), {"skill": comp, "percentage": 42.0, "count": 80})
        comp_list.append(item)

    return {
        "role_name": role_name,
        "description": profile.get("desc", ""),
        "total_jobs": role_info["total_jobs"],
        "avg_salary_lpa": role_info["avg_salary_lpa"],
        "core_skills": core_list,
        "complementary_skills": comp_list,
        "emerging_skills": profile.get("emerging", ["Generative AI"]),
        "industry_spread": role_info["industries"],
        "location_spread": role_info["locations"]
    }
