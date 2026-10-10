"""
Personalized Skill Gap and Career Recommender Service
Team: Syntax Society
"""

from typing import List, Dict, Any
from utils.constants import ROLE_SKILL_PROFILES
from utils.normalizer import normalize_skill

CURATED_RESOURCES = {
    "Python": ["Python Official Docs & Tutorial", "Automate the Boring Stuff with Python", "LeetCode Python 75"],
    "SQL": ["Mode Analytics SQL Tutorial", "SQLZoo Interactive Drills", "LeetCode 50 SQL Study Plan"],
    "Power BI": ["Microsoft Learn Power BI Data Analyst Path", "Maven Analytics Power BI Masterclass"],
    "Tableau": ["Tableau Free Training Videos", "Kaggle Data Visualization Microcourse"],
    "Pandas": ["Pandas Official Cookbook", "Kaggle Pandas Course", "Wes McKinney: Python for Data Analysis"],
    "Machine Learning": ["Andrew Ng: Machine Learning Specialization", "Scikit-Learn User Guide", "Fast.ai Practical Deep Learning"],
    "Deep Learning": ["DeepLearning.AI Neural Networks and Deep Learning", "PyTorch 60-Minute Blitz"],
    "Generative AI": ["DeepLearning.AI Generative AI for Everyone", "Hugging Face Generative AI Course"],
    "RAG": ["LangChain RAG Architecture Guide", "LlamaIndex Documentation & Recipes"],
    "LLMs": ["Andrej Karpathy: State of GPT", "Hugging Face Transformers NLP Course"],
    "AWS": ["AWS Skill Builder Cloud Practitioner Essentials", "Stephane Maarek AWS Solutions Architect Course"],
    "Docker": ["Docker Official Getting Started Guide", "Play with Docker Interactive Labs"],
    "Kubernetes": ["Kubernetes The Hard Way by Kelsey Hightower", "Mumshad Mannambeth CKA Course"],
    "React": ["React.dev Official Interactive Tutorial", "Full Stack Open (University of Helsinki)"],
    "FastAPI": ["FastAPI Official Tutorial by Sebastián Ramírez", "TestDriven.io Microservices with FastAPI"],
    "PostgreSQL": ["PostgreSQL Tutorial (postgresqltutorial.com)", "Use The Index, Luke! SQL Indexing Guide"],
    "MLOps": ["Made With ML (Goku Mohandas)", "Coursera MLOps Specialization by Andrew Ng"],
    "Vector Databases": ["Pinecone Vector Database Architecture Guide", "Chroma DB Quickstart"],
    "Cybersecurity": ["TryHackMe Pre-Security Path", "OWASP Top 10 Security Risks Guide"]
}

def recommend_skills(target_role: str, user_skills_input: List[str], experience_level: str = "Fresher") -> Dict[str, Any]:
    """
    Computes a personalized skill gap analysis, match score, and structured learning roadmap.
    """
    # Normalize user skills
    normalized_user_skills = set()
    for s in user_skills_input:
        norm = normalize_skill(s)
        if norm:
            normalized_user_skills.add(norm)

    profile = ROLE_SKILL_PROFILES.get(target_role, ROLE_SKILL_PROFILES["Python Developer"])
    core_skills = profile["core"]
    comp_skills = profile["complementary"]
    emerging_skills = profile.get("emerging", ["Generative AI"])

    # Categorize user status
    matched_core = [s for s in core_skills if s in normalized_user_skills]
    missing_core = [s for s in core_skills if s not in normalized_user_skills]

    matched_comp = [s for s in comp_skills if s in normalized_user_skills]
    missing_comp = [s for s in comp_skills if s not in normalized_user_skills]

    matched_emerging = [s for s in emerging_skills if s in normalized_user_skills]
    missing_emerging = [s for s in emerging_skills if s not in normalized_user_skills]

    # Weighted match calculation
    total_core_wt = 60.0
    total_comp_wt = 25.0
    total_emerging_wt = 15.0

    core_score = (len(matched_core) / max(1, len(core_skills))) * total_core_wt
    comp_score = (len(matched_comp) / max(1, len(comp_skills))) * total_comp_wt
    emerging_score = (len(matched_emerging) / max(1, len(emerging_skills))) * total_emerging_wt

    raw_match_pct = round(core_score + comp_score + emerging_score, 1)

    # Readiness level
    if raw_match_pct >= 80:
        readiness_badge = "Market Leader (Highly Competitive)"
        readiness_color = "#10b981"
    elif raw_match_pct >= 55:
        readiness_badge = "Interview Ready (Minor Gaps)"
        readiness_color = "#6366f1"
    elif raw_match_pct >= 30:
        readiness_badge = "Foundational Stage (Core Gaps)"
        readiness_color = "#f59e0b"
    else:
        readiness_badge = "Beginner (Requires Fundamental Upskilling)"
        readiness_color = "#ef4444"

    # Prioritize recommended next skills
    recommended_next = []
    # 1. Missing core skills take first priority
    for s in missing_core[:3]:
        recommended_next.append(s)
    # 2. Add an emerging skill for competitive edge
    if missing_emerging:
        recommended_next.append(missing_emerging[0])
    # 3. Add complementary skill
    if missing_comp and len(recommended_next) < 5:
        recommended_next.append(missing_comp[0])

    # Build actionable roadmap steps
    roadmap = []
    step_num = 1
    for s in recommended_next:
        if s in core_skills:
            importance = "Critical Core"
            why = f"Fundamental prerequisite requested in >80% of {target_role} vacancies."
            weeks = 3
        elif s in emerging_skills:
            importance = "Emerging Edge"
            why = f"High-growth multiplier that differentiates you from average applicants in future hiring cycles."
            weeks = 4
        else:
            importance = "High-Impact"
            why = f"Essential for end-to-end tooling and production workflow integration."
            weeks = 2

        resources = CURATED_RESOURCES.get(s, [f"Official documentation and tutorials for {s}", f"Practical projects building with {s}"])

        roadmap.append({
            "step_number": step_num,
            "skill": s,
            "importance": importance,
            "why_needed": why,
            "estimated_weeks": weeks,
            "recommended_resources": resources
        })
        step_num += 1

    # Format chart radar data
    # Compare proficiency / presence across 6 key pillars
    chart_pillars = ["Core Programming", "Data/Algorithms", "Frameworks", "Cloud & Infra", "Databases", "Frontier AI"]
    required_benchmark = [90, 85, 80, 75, 85, 70]
    
    # Estimate user score per pillar based on user's skills
    pillar_scores = []
    for idx, p in enumerate(chart_pillars):
        factor = min(1.0, (len(normalized_user_skills) + (idx % 2)) / 6.0)
        user_val = int(min(95, max(20, round(required_benchmark[idx] * (factor * 0.8 + (raw_match_pct / 200))))))
        pillar_scores.append(user_val)

    return {
        "target_role": target_role,
        "match_percentage": raw_match_pct,
        "readiness_badge": readiness_badge,
        "readiness_color": readiness_color,
        "matched_skills": sorted(list(normalized_user_skills.intersection(set(core_skills + comp_skills + emerging_skills)))),
        "missing_core_skills": missing_core,
        "missing_complementary_skills": missing_comp,
        "missing_emerging_skills": missing_emerging,
        "recommended_next_skills": recommended_next,
        "learning_roadmap": roadmap,
        "skill_gap_summary": {
            "core_completed": f"{len(matched_core)}/{len(core_skills)}",
            "complementary_completed": f"{len(matched_comp)}/{len(comp_skills)}",
            "emerging_completed": f"{len(matched_emerging)}/{len(emerging_skills)}",
            "radar_pillars": chart_pillars,
            "benchmark_scores": required_benchmark,
            "user_scores": pillar_scores
        }
    }
