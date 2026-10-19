"""
Analytics Aggregation Service for SkillPulse Bharat
Unifies executive metrics for the Analytics-Driven Decision Support Dashboard.
Team: Syntax Society
"""

from typing import Dict, Any, List
from services.data_service import data_service
from services.scoring import calculate_skillpulse_score, EMERGING_FRONTIER_SKILLS

def get_executive_dashboard_kpis() -> Dict[str, Any]:
    """
    Computes top-level KPIs from real labor market benchmark datasets.
    """
    aj = data_service.get_analytics_jobs()
    ds = data_service.get_datascience_jobs()
    skills_freq = data_service.get_skill_frequencies()

    total_jobs = len(aj)  # 15,841
    total_skills = len(skills_freq)

    # Top skill
    sorted_skills = sorted(skills_freq.items(), key=lambda x: x[1], reverse=True)
    top_skill_tuple = sorted_skills[0] if sorted_skills else ("SQL", 1009)

    # Average salary from sample
    avg_salary_lpa = round(float(aj["parsed_salary_lpa"].mean()), 1)
    median_salary_lpa = round(float(aj["parsed_salary_lpa"].median()), 1)

    # Top hiring role
    top_role = ds["job_title_clean"].value_counts().index[0]

    # Benchmark SkillPulse score for top skill
    top_sp = calculate_skillpulse_score(top_skill_tuple[0])

    # Top 10 skills formatted
    top_10 = []
    for sk, cnt in sorted_skills[:12]:
        sp = calculate_skillpulse_score(sk)
        top_10.append({
            "skill": sk,
            "count": cnt,
            "percentage": round((cnt / total_jobs) * 100, 1),
            "skillpulse_score": sp["skillpulse_score"],
            "avg_salary_lpa": sp["empirical_metrics"]["avg_associated_salary_lpa"]
        })

    return {
        "total_jobs_analyzed": total_jobs,
        "additional_ds_postings": len(ds),
        "total_skills_identified": total_skills,
        "top_skill_name": top_skill_tuple[0],
        "top_skill_count": top_skill_tuple[1],
        "avg_salary_lpa": avg_salary_lpa,
        "median_salary_lpa": median_salary_lpa,
        "top_hiring_role": top_role,
        "benchmark_skillpulse_score": top_sp["skillpulse_score"],
        "top_skills_table": top_10
    }

from services.emerging_service import emerging_service

def get_emerging_skills_catalog() -> List[Dict[str, Any]]:
    """
    Daily future-facing market signals dynamically synthesized by emerging_service.
    Reflects 24-hour deltas, momentum waves, and 7-day sparkline histories.
    """
    items = emerging_service.get_catalog_with_daily_metrics()
    result = []
    for item in items[:8]:  # Top 8 frontier skills for executive radar
        roles = ", ".join(item.get("target_roles", [])) if isinstance(item.get("target_roles"), list) else str(item.get("target_roles", ""))
        result.append({
            "skill": item["skill_name"],
            "category": item["category"],
            "signal_strength": item["signal_strength"],
            "market_role_fit": roles,
            "description": item["description"],
            "status": item["adoption_stage"],
            "daily_delta_pct": item["daily_delta_pct"],
            "trend_direction": item["trend_direction"],
            "velocity_label": item["velocity_label"],
            "growth_rate_pct": item["growth_rate_pct"],
            "history_7d": item["history_7d"],
            "as_of_date": item["as_of_date"],
            "disclaimer": "[DAILY SIGNAL ENGINE] Market momentum index updated daily; analytical signal based on enterprise hiring trends."
        })
    return result
