"""
Market and Salary Intelligence Service for SkillPulse Bharat
Extracts empirical compensation structures, company hiring trends, and role dynamics.
Uses DataScience Jobs.csv (1,602 rows) and Analytics Jobs.csv (15,841 rows).
Team: Syntax Society
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from services.data_service import data_service

def get_salary_vs_experience() -> List[Dict[str, Any]]:
    """
    Computes compensation progression across experience tiers.
    [OBSERVED DATA from Analytics Jobs]
    """
    df = data_service.get_analytics_jobs()
    valid = df.dropna(subset=["avg_exp", "parsed_salary_lpa"]).copy()

    # Define bins
    bins = [0, 2, 5, 8, 12, 30]
    labels = ["0-2 yrs (Fresher/Entry)", "2-5 yrs (Junior)", "5-8 yrs (Mid-Level)", "8-12 yrs (Senior)", "12+ yrs (Lead/Principal)"]
    valid["exp_band"] = pd.cut(valid["avg_exp"], bins=bins, labels=labels, right=True)

    grouped = valid.groupby("exp_band", observed=False)["parsed_salary_lpa"].agg(
        avg_salary="mean",
        median_salary="median",
        min_salary="min",
        max_salary="max",
        job_count="count"
    ).reset_index()

    result = []
    for _, r in grouped.iterrows():
        if pd.notna(r["avg_salary"]):
            result.append({
                "experience_band": str(r["exp_band"]),
                "avg_salary_lpa": round(float(r["avg_salary"]), 1),
                "median_salary_lpa": round(float(r["median_salary"]), 1),
                "min_salary_lpa": round(float(r["min_salary"]), 1),
                "max_salary_lpa": round(float(r["max_salary"]), 1),
                "job_count": int(r["job_count"])
            })
    return result

def get_salary_bracket_distribution() -> List[Dict[str, Any]]:
    """
    Volume of jobs in each compensation bracket.
    [OBSERVED DATA from Analytics Jobs]
    """
    df = data_service.get_analytics_jobs()
    counts = df["salary"].value_counts().to_dict()
    total = len(df)

    display_order = ["0to3", "3to6", "6to10", "10to15", "15to25", "25to50"]
    labels_map = {
        "0to3": "₹0 - 3 LPA",
        "3to6": "₹3 - 6 LPA",
        "6to10": "₹6 - 10 LPA",
        "10to15": "₹10 - 15 LPA",
        "15to25": "₹15 - 25 LPA",
        "25to50": "₹25 - 50 LPA"
    }

    result = []
    for b in display_order:
        cnt = counts.get(b, 0)
        result.append({
            "bracket_code": b,
            "label": labels_map.get(b, b),
            "job_count": int(cnt),
            "percentage": round((cnt / total) * 100, 1) if total > 0 else 0.0
        })
    return result

def get_top_hiring_companies(limit: int = 15) -> List[Dict[str, Any]]:
    """
    Ranks companies from DataScience Jobs dataset by total hiring volume.
    [OBSERVED DATA from DataScience Jobs]
    """
    df = data_service.get_datascience_jobs()
    grouped = df.groupby("company_name_clean").agg(
        total_openings=("num_of_jobs_clean", "sum"),
        posting_records=("job_title_clean", "count"),
        avg_salary=("avg_salary_lpa", "mean"),
        min_salary=("min_salary_lpa", "min"),
        max_salary=("max_salary_lpa", "max"),
        min_exp=("min_experience_clean", "mean"),
        job_titles=("job_title_clean", lambda s: list(set(s)))
    ).reset_index()

    grouped = grouped.sort_values(by="total_openings", ascending=False).head(limit)

    results = []
    for _, r in grouped.iterrows():
        results.append({
            "company": r["company_name_clean"],
            "total_openings": int(r["total_openings"]),
            "posting_records": int(r["posting_records"]),
            "avg_salary_lpa": round(float(r["avg_salary"]), 1) if pd.notna(r["avg_salary"]) else None,
            "salary_range": f"{r['min_salary']:.1f}L - {r['max_salary']:.1f}L" if pd.notna(r["min_salary"]) else "N/A",
            "avg_min_exp": round(float(r["min_exp"]), 1) if pd.notna(r["min_exp"]) else 2.0,
            "job_titles": r["job_titles"][:4]
        })
    return results

def get_company_profile(company_name: str) -> Optional[Dict[str, Any]]:
    """
    Deep profile for a selected company.
    """
    df = data_service.get_datascience_jobs()
    sub = df[df["company_name_clean"].str.lower() == company_name.strip().lower()]
    if sub.empty:
        # Fallback partial match
        sub = df[df["company_name_clean"].str.contains(company_name.strip(), case=False, na=False)]
    if sub.empty:
        return None

    actual_name = sub["company_name_clean"].iloc[0]
    total_jobs = int(sub["num_of_jobs_clean"].sum())
    avg_sal = round(float(sub["avg_salary_lpa"].mean()), 1)
    min_sal = round(float(sub["min_salary_lpa"].min()), 1)
    max_sal = round(float(sub["max_salary_lpa"].max()), 1)
    avg_exp = round(float(sub["min_experience_clean"].mean()), 1)

    roles = sub.groupby("job_title_clean")["num_of_jobs_clean"].sum().reset_index()
    roles_list = [{"title": r["job_title_clean"], "openings": int(r["num_of_jobs_clean"])} for _, r in roles.iterrows()]

    return {
        "company": actual_name,
        "total_openings": total_jobs,
        "avg_salary_lpa": avg_sal,
        "min_salary_lpa": min_sal,
        "max_salary_lpa": max_sal,
        "avg_min_exp": avg_exp,
        "roles_offered": roles_list
    }

def get_role_salary_patterns() -> List[Dict[str, Any]]:
    """
    Role-level compensation averages from DataScience Jobs.
    """
    df = data_service.get_datascience_jobs()
    grouped = df.groupby("job_title_clean").agg(
        openings=("num_of_jobs_clean", "sum"),
        avg_sal=("avg_salary_lpa", "mean"),
        min_sal=("min_salary_lpa", "min"),
        max_sal=("max_salary_lpa", "max"),
        avg_exp=("min_experience_clean", "mean")
    ).reset_index()

    grouped = grouped.sort_values(by="avg_sal", ascending=False)
    results = []
    for _, r in grouped.iterrows():
        results.append({
            "role": r["job_title_clean"],
            "openings": int(r["openings"]),
            "avg_salary_lpa": round(float(r["avg_sal"]), 1),
            "salary_range": f"{r['min_sal']:.1f}L - {r['max_sal']:.1f}L",
            "avg_min_exp": round(float(r["avg_exp"]), 1)
        })
    return results

def get_skill_salary_associations() -> List[Dict[str, Any]]:
    """
    Analyzes sample salary associated with key skills.
    DISCLAIMER: Association in sample, NOT causal.
    """
    df = data_service.get_analytics_jobs()
    baseline = 12.27

    target_skills = [
        "Machine Learning", "Deep Learning", "Python", "SQL", "Big Data",
        "SAS", "Tableau", "Power BI", "Excel", "Data Analysis", "Java", "AWS"
    ]

    results = []
    for sk in target_skills:
        pattern = rf"(?i)\b{re_escape(sk)}\b"
        sub = df[df["key_skills"].fillna("").str.contains(pattern, regex=True)]
        count = len(sub)
        if count >= 10:
            sal_mean = round(float(sub["parsed_salary_lpa"].mean()), 1)
            sal_median = round(float(sub["parsed_salary_lpa"].median()), 1)
            diff_pct = round(((sal_mean - baseline) / baseline) * 100, 1)
            results.append({
                "skill": sk,
                "sample_postings": count,
                "associated_avg_salary_lpa": sal_mean,
                "associated_median_salary_lpa": sal_median,
                "baseline_difference_pct": diff_pct,
                "note": "Associated with higher-paying postings" if diff_pct > 0 else "Baseline market range"
            })

    results.sort(key=lambda x: x["associated_avg_salary_lpa"], reverse=True)
    return results

def re_escape(s: str) -> str:
    import re
    return re.escape(s)
