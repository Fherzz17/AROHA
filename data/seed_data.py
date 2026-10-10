"""
Data Seed and Generation Engine for SkillPulse Bharat
Generates a realistic benchmark dataset of Indian Tech Job Postings.
Team: Syntax Society
"""

import json
import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.constants import (
    ROLE_SKILL_PROFILES,
    TARGET_ROLES,
    INDIAN_LOCATIONS,
    INDUSTRIES,
    TOP_COMPANIES,
    SKILL_TAXONOMY
)

DATA_DIR = Path(__file__).parent
DB_PATH = DATA_DIR / "job_market.db"
JSON_PATH = DATA_DIR / "sample_jobs.json"

QUARTERS = [
    ("2024-Q1", "2024-01-01", "2024-03-31"),
    ("2024-Q2", "2024-04-01", "2024-06-30"),
    ("2024-Q3", "2024-07-01", "2024-09-30"),
    ("2024-Q4", "2024-10-01", "2024-12-31"),
    ("2025-Q1", "2025-01-01", "2025-03-31"),
    ("2025-Q2", "2025-04-01", "2025-06-30"),
    ("2025-Q3", "2025-07-01", "2025-09-30")
]

# Weight multiplier for emerging skills over time (shows surging adoption of GenAI, RAG, etc.)
EMERGING_QUARTER_MULTIPLIER = {
    "2024-Q1": 0.15,
    "2024-Q2": 0.30,
    "2024-Q3": 0.50,
    "2024-Q4": 0.70,
    "2025-Q1": 0.90,
    "2025-Q2": 1.15,
    "2025-Q3": 1.45
}

def generate_job_postings(count: int = 1800) -> List[Dict[str, Any]]:
    random.seed(42)  # Deterministic seed for reproducible evaluation
    jobs = []

    for i in range(1, count + 1):
        role = random.choice(TARGET_ROLES)
        profile = ROLE_SKILL_PROFILES[role]
        company = random.choice(TOP_COMPANIES)
        industry = random.choice(INDUSTRIES)
        location = random.choice(INDIAN_LOCATIONS)
        
        # Quarter distribution
        quarter_info = random.choice(QUARTERS)
        q_label, start_dt_str, end_dt_str = quarter_info
        start_dt = datetime.strptime(start_dt_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_dt_str, "%Y-%m-%d")
        random_days = random.randint(0, (end_dt - start_dt).days)
        post_date = (start_dt + timedelta(days=random_days)).strftime("%Y-%m-%d")

        # Experience & Salary (LPA)
        exp_years = random.choices([0, 1, 2, 3, 4, 5, 6, 7], weights=[15, 20, 25, 18, 10, 6, 4, 2])[0]
        base_salary = 4.5 + (exp_years * 2.8) + random.uniform(-1.5, 3.5)
        if "AI/ML" in role or "Data Scientist" in role:
            base_salary += random.uniform(2.0, 5.0)
        salary_lpa = round(max(3.6, min(base_salary, 48.0)), 1)

        # Select skills
        # Core skills: Pick 3-5
        selected_skills = set(random.sample(profile["core"], min(len(profile["core"]), random.randint(3, 5))))
        # Complementary skills: Pick 1-3
        selected_skills.update(random.sample(profile["complementary"], min(len(profile["complementary"]), random.randint(1, 3))))

        # Emerging skills: probability depends on quarter multiplier
        mult = EMERGING_QUARTER_MULTIPLIER.get(q_label, 0.5)
        if random.random() < (0.25 * mult):
            emerging_candidates = profile.get("emerging", ["Generative AI"])
            selected_skills.add(random.choice(emerging_candidates))
            if random.random() < 0.35 and len(emerging_candidates) > 1:
                selected_skills.add(random.choice(emerging_candidates))

        # Occasionally add cloud or common tooling
        if random.random() < 0.4:
            selected_skills.add(random.choice(["AWS", "Docker", "Git", "SQL", "Linux"]))

        skills_list = sorted(list(selected_skills))

        # Synthesize realistic job description
        skills_str = ", ".join(skills_list[:4])
        desc = (
            f"{company} is hiring a passionate {role} in {location}. "
            f"Candidate should have {exp_years}+ years of hands-on experience working with {skills_str}. "
            f"The role involves architecting solutions in our {industry} division with high scalability."
        )

        job = {
            "id": i,
            "job_title": role,
            "company": company,
            "industry": industry,
            "location": location,
            "date": post_date,
            "quarter": q_label,
            "experience_years": exp_years,
            "salary_lpa": salary_lpa,
            "skills": skills_list,
            "description": desc
        }
        jobs.append(job)

    return jobs

def seed_database(force: bool = False) -> None:
    """Creates SQLite database and populates with seed jobs."""
    if DB_PATH.exists() and not force:
        # Check if already populated
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='jobs'")
        table_exists = cursor.fetchone()[0]
        if table_exists:
            cursor.execute("SELECT count(*) FROM jobs")
            count = cursor.fetchone()[0]
            conn.close()
            if count > 500:
                print(f"[Seed] Database already populated with {count} records at {DB_PATH}")
                return

    print("[Seed] Generating benchmark Indian tech job dataset...")
    jobs = generate_job_postings(1800)

    # Save to JSON
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)
    print(f"[Seed] Saved {len(jobs)} jobs to {JSON_PATH}")

    # Save to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS job_skills")
    cursor.execute("DROP TABLE IF EXISTS jobs")

    cursor.execute("""
    CREATE TABLE jobs (
        id INTEGER PRIMARY KEY,
        job_title TEXT NOT NULL,
        company TEXT NOT NULL,
        industry TEXT NOT NULL,
        location TEXT NOT NULL,
        date TEXT NOT NULL,
        quarter TEXT NOT NULL,
        experience_years INTEGER NOT NULL,
        salary_lpa REAL NOT NULL,
        description TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE job_skills (
        job_id INTEGER,
        skill TEXT NOT NULL,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )
    """)

    cursor.execute("CREATE INDEX idx_jobs_title ON jobs(job_title)")
    cursor.execute("CREATE INDEX idx_jobs_quarter ON jobs(quarter)")
    cursor.execute("CREATE INDEX idx_jobs_industry ON jobs(industry)")
    cursor.execute("CREATE INDEX idx_job_skills_skill ON job_skills(skill)")

    for j in jobs:
        cursor.execute("""
        INSERT INTO jobs (id, job_title, company, industry, location, date, quarter, experience_years, salary_lpa, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            j["id"], j["job_title"], j["company"], j["industry"], j["location"],
            j["date"], j["quarter"], j["experience_years"], j["salary_lpa"], j["description"]
        ))

        for s in j["skills"]:
            cursor.execute("INSERT INTO job_skills (job_id, skill) VALUES (?, ?)", (j["id"], s))

    conn.commit()
    conn.close()
    print(f"[Seed] Successfully seeded {len(jobs)} jobs into SQLite database at {DB_PATH}")

if __name__ == "__main__":
    seed_database(force=True)
