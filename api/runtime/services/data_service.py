"""
Data Service for AROHA AI Workforce Intelligence Platform
Loads, cleans, and standardizes the core benchmark datasets:
1. Analytics Jobs.csv (15,841 postings)
2. DataScience Jobs.csv (1,602 postings)
3. JDS Skill Traits.xlsx (139 junior data scientists)
4. SDS Personality Traits.xlsx (161 senior data scientists)
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
from utils.normalizer import normalize_skill

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ANALYTICS_CSV = DATA_DIR / "Analytics Jobs.csv"
DATASCIENCE_CSV = DATA_DIR / "DataScience Jobs.csv"
JDS_XLSX = DATA_DIR / "JDS Skill Traits.xlsx"
SDS_XLSX = DATA_DIR / "SDS Personality Traits.xlsx"

# Salary bracket mapping (LPA midpoints)
SALARY_BRACKET_MAP = {
    "0to3": 1.5,
    "3to6": 4.5,
    "6to10": 8.0,
    "10to15": 12.5,
    "15to25": 20.0,
    "25to50": 37.5
}

def parse_salary_bracket(val: Any) -> Optional[float]:
    if pd.isna(val):
        return None
    s = str(val).lower().replace(" ", "")
    if s in SALARY_BRACKET_MAP:
        return SALARY_BRACKET_MAP[s]
    m = re.match(r"(\d+)to(\d+)", s)
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2.0
    return None

def parse_experience_years(val: Any) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Returns (min_exp, max_exp, avg_exp)."""
    if pd.isna(val):
        return None, None, None
    s = str(val).lower().replace("yrs", "").replace("yr", "").strip()
    m = re.match(r"(\d+)-(\d+)", s)
    if m:
        mn, mx = float(m.group(1)), float(m.group(2))
        return mn, mx, (mn + mx) / 2.0
    m_single = re.match(r"(\d+)", s)
    if m_single:
        v = float(m_single.group(1))
        return v, v, v
    return None, None, None

def parse_lpa_string(val: Any) -> Optional[float]:
    if pd.isna(val):
        return None
    s = str(val).upper().replace("L", "").replace("₹", "").strip()
    try:
        return float(s)
    except:
        return None

class DataService:
    def __init__(self):
        self._analytics_df: Optional[pd.DataFrame] = None
        self._datascience_df: Optional[pd.DataFrame] = None
        self._jds_df: Optional[pd.DataFrame] = None
        self._sds_df: Optional[pd.DataFrame] = None
        self._skills_freq: Optional[Dict[str, int]] = None

    def get_analytics_jobs(self) -> pd.DataFrame:
        if self._analytics_df is None:
            df = pd.read_csv(ANALYTICS_CSV)
            # Clean and derive columns
            df["parsed_salary_lpa"] = df["salary"].apply(parse_salary_bracket)
            exp_parsed = df["experience"].apply(parse_experience_years)
            df["min_exp"] = [p[0] for p in exp_parsed]
            df["max_exp"] = [p[1] for p in exp_parsed]
            df["avg_exp"] = [p[2] for p in exp_parsed]
            df["job_desig_clean"] = df["job_desig"].fillna("Other").astype(str).str.strip()
            df["location_clean"] = df["location"].fillna("India").astype(str).str.strip()
            self._analytics_df = df
        return self._analytics_df

    def get_datascience_jobs(self) -> pd.DataFrame:
        if self._datascience_df is None:
            df = pd.read_csv(DATASCIENCE_CSV)
            df["avg_salary_lpa"] = df["avg_salary"].apply(parse_lpa_string)
            df["min_salary_lpa"] = df["min_salary"].apply(parse_lpa_string)
            df["max_salary_lpa"] = df["max_salary"].apply(parse_lpa_string)
            df["num_of_jobs_clean"] = pd.to_numeric(df["num_of_jobs"], errors="coerce").fillna(1).astype(int)
            df["company_name_clean"] = df["company_name"].fillna("Unknown Company").astype(str).str.strip()
            df["job_title_clean"] = df["job_title"].fillna("Data Scientist").astype(str).str.strip()
            df["min_experience_clean"] = pd.to_numeric(df["min_experience"], errors="coerce").fillna(2).astype(float)
            self._datascience_df = df
        return self._datascience_df

    def get_jds_traits(self) -> pd.DataFrame:
        if self._jds_df is None:
            df = pd.read_excel(JDS_XLSX)
            df.columns = [c.strip().lower() for c in df.columns]
            self._jds_df = df
        return self._jds_df

    def get_sds_traits(self) -> pd.DataFrame:
        if self._sds_df is None:
            df = pd.read_excel(SDS_XLSX)
            df.columns = [c.strip().lower() for c in df.columns]
            # Standardize target column name
            for col in df.columns:
                if "success" in col:
                    df.rename(columns={col: "success_classification_high_low"}, inplace=True)
                    break
            self._sds_df = df
        return self._sds_df

    def get_skill_frequencies(self) -> Dict[str, int]:
        """Parses and normalizes skills from Analytics Jobs key_skills."""
        if self._skills_freq is None:
            df = self.get_analytics_jobs()
            freq: Dict[str, int] = {}
            for row in df["key_skills"].dropna():
                parts = [p.strip() for p in str(row).replace("|", ",").replace(";", ",").split(",")]
                seen_in_job = set()
                for p in parts:
                    if len(p) < 2 or p == "...":
                        continue
                    norm = normalize_skill(p)
                    if norm and len(norm) > 1 and norm != "..." and norm not in seen_in_job:
                        freq[norm] = freq.get(norm, 0) + 1
                        seen_in_job.add(norm)
            self._skills_freq = freq
        return self._skills_freq

    def get_data_quality_report(self) -> Dict[str, Any]:
        """Returns structured data quality metrics for SAS evaluation."""
        aj = self.get_analytics_jobs()
        ds = self.get_datascience_jobs()
        jds = self.get_jds_traits()
        sds = self.get_sds_traits()
        skills = self.get_skill_frequencies()

        return {
            "analytics_jobs": {
                "rows": len(aj),
                "columns": len(aj.columns),
                "missing_values": int(aj.isnull().sum().sum()),
                "salary_coverage_pct": round((aj["parsed_salary_lpa"].notnull().sum() / len(aj)) * 100, 1),
                "unique_designations": int(aj["job_desig_clean"].nunique()),
                "unique_skills_extracted": len(skills),
                "median_salary_lpa": float(aj["parsed_salary_lpa"].median()),
                "avg_salary_lpa": round(float(aj["parsed_salary_lpa"].mean()), 2)
            },
            "datascience_jobs": {
                "rows": len(ds),
                "columns": len(ds.columns),
                "companies": int(ds["company_name_clean"].nunique()),
                "unique_roles": int(ds["job_title_clean"].nunique()),
                "avg_salary_lpa": round(float(ds["avg_salary_lpa"].mean()), 2),
                "salary_range": f"{ds['min_salary_lpa'].min():.1f}L - {ds['max_salary_lpa'].max():.1f}L"
            },
            "jds_skill_traits": {
                "samples": len(jds),
                "features": ["big_data_skills", "maths-stats_skills", "coding_skills", "ai_and_ml_skills", "dashboard_and_storytelling_skills"],
                "target": "salary_hike_high_or_low",
                "high_hike_ratio": round(float(jds["salary_hike_high_or_low"].mean()) * 100, 1)
            },
            "sds_personality_traits": {
                "samples": len(sds),
                "features": ["neuroticism", "extraversion", "openness_to_experience", "agreeableness", "conscientiousness"],
                "target": "success_classification_high_low",
                "success_ratio": round(float(sds["success_classification_high_low"].mean()) * 100, 1)
            }
        }

# Global singleton
data_service = DataService()
