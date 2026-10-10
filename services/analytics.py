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

def get_emerging_skills_catalog() -> List[Dict[str, Any]]:
    """
    Future-facing market signals.
    DISCLAIMER: The supplied job-market snapshot does not contain posting dates.
    Future-facing signals are analytical/illustrative and are not guaranteed forecasts.
    """
    return [
        {
            "skill": "Generative AI",
            "category": "Frontier AI",
            "signal_strength": 98,
            "market_role_fit": "Data Scientist, AI/ML Engineer",
            "description": "Foundation models, LLM orchestration, synthetic data, enterprise conversational intelligence.",
            "status": "Rapid Market Expansion",
            "disclaimer": "[ANALYTICAL SIGNAL] Emerging future signal; not a guaranteed forecast."
        },
        {
            "skill": "RAG (Retrieval-Augmented Generation)",
            "category": "Frontier AI",
            "signal_strength": 96,
            "market_role_fit": "AI/ML Engineer, Data Scientist",
            "description": "Connecting LLMs to enterprise databases, vector embeddings, and private document knowledge.",
            "status": "High Industry Adoption",
            "disclaimer": "[ANALYTICAL SIGNAL] Emerging future signal; not a guaranteed forecast."
        },
        {
            "skill": "LLMs & Fine-Tuning",
            "category": "Frontier AI",
            "signal_strength": 95,
            "market_role_fit": "AI/ML Engineer, Data Scientist",
            "description": "Adaptation, evaluation, quantization, and prompt engineering for open and closed language models.",
            "status": "High Industry Adoption",
            "disclaimer": "[ANALYTICAL SIGNAL] Emerging future signal; not a guaranteed forecast."
        },
        {
            "skill": "MLOps",
            "category": "AI Infrastructure",
            "signal_strength": 92,
            "market_role_fit": "Data Engineer, AI/ML Engineer",
            "description": "Automated pipelines, model monitoring, drift tracking, GPU scaling, and model registry.",
            "status": "Production Standard",
            "disclaimer": "[ANALYTICAL SIGNAL] Emerging future signal; not a guaranteed forecast."
        },
        {
            "skill": "Vector Databases",
            "category": "Data Infrastructure",
            "signal_strength": 90,
            "market_role_fit": "Data Engineer, AI/ML Engineer",
            "description": "High-dimensional embeddings retrieval (Pinecone, Chroma, Qdrant, Milvus).",
            "status": "High Industry Adoption",
            "disclaimer": "[ANALYTICAL SIGNAL] Emerging future signal; not a guaranteed forecast."
        },
        {
            "skill": "Agentic AI",
            "category": "Frontier AI",
            "signal_strength": 95,
            "market_role_fit": "AI/ML Engineer, Software Developer",
            "description": "Autonomous multi-agent systems with tool use, planning loops, and memory architectures.",
            "status": "Frontier Innovation",
            "disclaimer": "[ANALYTICAL SIGNAL] Emerging future signal; not a guaranteed forecast."
        },
        {
            "skill": "Cloud Security",
            "category": "Architecture & Security",
            "signal_strength": 87,
            "market_role_fit": "Cloud Architect, DevOps Engineer",
            "description": "Zero trust architecture, IAM governance, container security, and compliance.",
            "status": "Core Enterprise Standard",
            "disclaimer": "[ANALYTICAL SIGNAL] Emerging future signal; not a guaranteed forecast."
        },
        {
            "skill": "Rust",
            "category": "Programming Languages",
            "signal_strength": 85,
            "market_role_fit": "Data Engineer, Systems Engineer",
            "description": "Memory-safe systems programming for high-throughput AI inference and data streaming.",
            "status": "Early High-Velocity Adoption",
            "disclaimer": "[ANALYTICAL SIGNAL] Emerging future signal; not a guaranteed forecast."
        }
    ]
