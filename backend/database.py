"""
Database Access Layer for SkillPulse Bharat
Provides modular query interfaces for SQLite benchmark storage.
Team: Syntax Society
"""

import os
import shutil
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "job_market.db"

def get_db_path() -> Path:
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        tmp_db = Path("/tmp") / "aroha_auth.db"
        if not tmp_db.exists() and PROJECT_DB_PATH.exists():
            try:
                shutil.copy2(PROJECT_DB_PATH, tmp_db)
            except Exception:
                return PROJECT_DB_PATH
        if tmp_db.exists():
            return tmp_db
    return PROJECT_DB_PATH

def get_connection() -> sqlite3.Connection:
    target_path = get_db_path()
    try:
        conn = sqlite3.connect(target_path)
    except sqlite3.OperationalError:
        conn = sqlite3.connect(f"file:{target_path.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def get_total_jobs_count() -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM jobs")
        return cursor.fetchone()[0]

def get_total_unique_skills_count() -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(DISTINCT skill) FROM job_skills")
        return cursor.fetchone()[0]

def get_top_skills(limit: int = 15) -> List[Dict[str, Any]]:
    total = get_total_jobs_count()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT skill, count(*) as job_count
            FROM job_skills
            GROUP BY skill
            ORDER BY job_count DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [
            {
                "skill": r["skill"],
                "count": r["job_count"],
                "percentage": round((r["job_count"] / total) * 100, 1) if total > 0 else 0
            }
            for r in rows
        ]

def get_skill_stats(skill_name: str) -> Optional[Dict[str, Any]]:
    total_jobs = get_total_jobs_count()
    with get_connection() as conn:
        cursor = conn.cursor()
        # Case-insensitive match on skill
        cursor.execute("""
            SELECT count(*) as count
            FROM job_skills
            WHERE lower(skill) = lower(?)
        """, (skill_name,))
        row = cursor.fetchone()
        if not row or row["count"] == 0:
            return None
        
        count = row["count"]
        pct = round((count / total_jobs) * 100, 1)

        # Top industries for this skill
        cursor.execute("""
            SELECT j.industry, count(*) as cnt
            FROM jobs j
            JOIN job_skills js ON j.id = js.job_id
            WHERE lower(js.skill) = lower(?)
            GROUP BY j.industry
            ORDER BY cnt DESC
            LIMIT 5
        """, (skill_name,))
        industries = [{"industry": r["industry"], "count": r["cnt"]} for r in cursor.fetchall()]

        # Related skills (co-occurrence)
        cursor.execute("""
            SELECT js2.skill as related_skill, count(*) as co_cnt
            FROM job_skills js1
            JOIN job_skills js2 ON js1.job_id = js2.job_id
            WHERE lower(js1.skill) = lower(?) AND lower(js2.skill) != lower(?)
            GROUP BY js2.skill
            ORDER BY co_cnt DESC
            LIMIT 6
        """, (skill_name, skill_name))
        related = [
            {
                "skill": r["related_skill"],
                "co_occurrences": r["co_cnt"],
                "correlation": round(min(0.99, r["co_cnt"] / max(1, count)), 2)
            }
            for r in cursor.fetchall()
        ]

        # Quarterly distribution
        cursor.execute("""
            SELECT j.quarter, count(*) as q_cnt
            FROM jobs j
            JOIN job_skills js ON j.id = js.job_id
            WHERE lower(js.skill) = lower(?)
            GROUP BY j.quarter
            ORDER BY j.quarter ASC
        """, (skill_name,))
        quarterly = [{"quarter": r["quarter"], "count": r["q_cnt"]} for r in cursor.fetchall()]

        return {
            "skill": skill_name,
            "count": count,
            "percentage": pct,
            "industries": industries,
            "related_skills": related,
            "quarterly": quarterly
        }

def get_role_details(role_name: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT count(*) as total, avg(salary_lpa) as avg_sal
            FROM jobs
            WHERE lower(job_title) = lower(?)
        """, (role_name,))
        meta = cursor.fetchone()
        if not meta or meta["total"] == 0:
            return None
        
        total_role_jobs = meta["total"]
        avg_salary = round(meta["avg_sal"] or 0.0, 1)

        # Top skills for role
        cursor.execute("""
            SELECT js.skill, count(*) as scnt
            FROM jobs j
            JOIN job_skills js ON j.id = js.job_id
            WHERE lower(j.job_title) = lower(?)
            GROUP BY js.skill
            ORDER BY scnt DESC
            LIMIT 12
        """, (role_name,))
        skills = [
            {
                "skill": r["skill"],
                "count": r["scnt"],
                "percentage": round((r["scnt"] / total_role_jobs) * 100, 1)
            }
            for r in cursor.fetchall()
        ]

        # Industry spread
        cursor.execute("""
            SELECT industry, count(*) as cnt
            FROM jobs
            WHERE lower(job_title) = lower(?)
            GROUP BY industry
            ORDER BY cnt DESC
            LIMIT 6
        """, (role_name,))
        industries = [{"industry": r["industry"], "count": r["cnt"]} for r in cursor.fetchall()]

        # Location spread
        cursor.execute("""
            SELECT location, count(*) as cnt
            FROM jobs
            WHERE lower(job_title) = lower(?)
            GROUP BY location
            ORDER BY cnt DESC
            LIMIT 6
        """, (role_name,))
        locations = [{"location": r["location"], "count": r["cnt"]} for r in cursor.fetchall()]

        return {
            "role": role_name,
            "total_jobs": total_role_jobs,
            "avg_salary_lpa": avg_salary,
            "top_skills": skills,
            "industries": industries,
            "locations": locations
        }

def get_all_skills_list() -> List[str]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT skill FROM job_skills ORDER BY skill ASC")
        return [r["skill"] for r in cursor.fetchall()]

def get_industry_distribution() -> List[Dict[str, Any]]:
    total = get_total_jobs_count()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT industry, count(*) as cnt, avg(salary_lpa) as avg_sal
            FROM jobs
            GROUP BY industry
            ORDER BY cnt DESC
        """)
        return [
            {
                "industry": r["industry"],
                "count": r["cnt"],
                "percentage": round((r["cnt"] / total) * 100, 1) if total > 0 else 0,
                "avg_salary": round(r["avg_sal"] or 0.0, 1)
            }
            for r in cursor.fetchall()
        ]

def get_all_jobs_with_skills(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetches all jobs aggregated with their associated skills list."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT j.id, j.job_title, j.company, j.industry, j.location, j.date,
                   j.quarter, j.experience_years, j.salary_lpa, j.description,
                   GROUP_CONCAT(js.skill, '|||') as skills_str
            FROM jobs j
            LEFT JOIN job_skills js ON j.id = js.job_id
            GROUP BY j.id
            ORDER BY j.date DESC
        """
        if limit:
            query += f" LIMIT {int(limit)}"
        cursor.execute(query)
        rows = cursor.fetchall()
        jobs = []
        for r in rows:
            skills = [s.strip() for s in r["skills_str"].split("|||") if s.strip()] if r["skills_str"] else []
            jobs.append({
                "id": r["id"],
                "job_title": r["job_title"],
                "company": r["company"],
                "industry": r["industry"],
                "location": r["location"],
                "date": r["date"],
                "quarter": r["quarter"],
                "experience_years": r["experience_years"],
                "salary_lpa": r["salary_lpa"],
                "description": r["description"],
                "skills": skills
            })
        return jobs

def get_unique_locations() -> List[str]:
    """Returns sorted unique location names from indexed jobs."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT location FROM jobs WHERE location IS NOT NULL AND location != '' ORDER BY location ASC")
        return [r["location"] for r in cursor.fetchall()]

def get_job_by_id(job_id: int) -> Optional[Dict[str, Any]]:
    """Returns details and skills for a single job by id."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        if not row:
            return None
        cursor.execute("SELECT skill FROM job_skills WHERE job_id = ?", (job_id,))
        skills = [r["skill"] for r in cursor.fetchall()]
        data = dict(row)
        data["skills"] = skills
        return data
