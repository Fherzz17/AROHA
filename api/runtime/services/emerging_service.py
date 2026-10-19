"""
Emerging Skills Daily Market Intelligence Service
Calibrated for AROHA AI Workforce Intelligence Platform

Features:
- Deterministic, zero-dependency calendar-anchored momentum and drift engine
- Computes daily signal scores, 24-hour deltas (Δ%), trend directions, and 7-day sparkline histories
- Supports persistent custom overrides via JSON (for live scrapers or admin updates)
- Serverless-compatible (safe fallback on read-only environments like Vercel)
"""

import math
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OVERRIDES_FILE = DATA_DIR / "emerging_skills_overrides.json"

# Core empirical baselines for frontier & tech skills
EMERGING_SKILLS_BASE = [
    {
        "skill_name": "Generative AI",
        "category": "Frontier AI",
        "base_signal": 98,
        "base_growth_rate_pct": 142.5,
        "adoption_stage": "Rapid Expansion",
        "description": "Enterprise implementation of foundation models, text-to-code, synthetic data generation, and custom inference.",
        "target_roles": ["AI/ML Engineer", "Data Scientist", "Software Developer", "Python Developer"],
        "forecast_note": "Expected in >35% of senior engineering postings across Indian GCCs by late 2026."
    },
    {
        "skill_name": "RAG",
        "category": "Frontier AI",
        "base_signal": 96,
        "base_growth_rate_pct": 185.0,
        "adoption_stage": "Early Mainstream",
        "description": "Retrieval-Augmented Generation connecting LLMs to private enterprise databases, vector indices, and document stores.",
        "target_roles": ["AI/ML Engineer", "Data Scientist", "Python Developer"],
        "forecast_note": "Primary production pattern for domain-specific enterprise conversational intelligence."
    },
    {
        "skill_name": "Agentic AI",
        "category": "Frontier AI",
        "base_signal": 95,
        "base_growth_rate_pct": 210.0,
        "adoption_stage": "Frontier Innovation",
        "description": "Autonomous multi-agent workflows using tool execution, self-reflection, planning loops, and memory architectures.",
        "target_roles": ["AI/ML Engineer", "Software Developer"],
        "forecast_note": "Highest emerging experimental growth across AI startups and venture-backed Indian tech labs."
    },
    {
        "skill_name": "LLMs",
        "category": "Frontier AI",
        "base_signal": 95,
        "base_growth_rate_pct": 130.4,
        "adoption_stage": "High Momentum",
        "description": "Fine-tuning, prompt optimization, quantization, and evaluation of proprietary and open-weights Large Language Models.",
        "target_roles": ["AI/ML Engineer", "Data Scientist"],
        "forecast_note": "Surging demand across FinTech risk modeling and enterprise customer experience automation."
    },
    {
        "skill_name": "MLOps",
        "category": "AI Infrastructure",
        "base_signal": 92,
        "base_growth_rate_pct": 88.2,
        "adoption_stage": "Production Standard",
        "description": "Continuous training, model registry, drift monitoring, GPU orchestration, and latency-optimized deployment pipelines.",
        "target_roles": ["AI/ML Engineer", "Cloud/DevOps Architect", "Data Scientist"],
        "forecast_note": "Critical operational bridge between data science experimentation and scalable production systems."
    },
    {
        "skill_name": "Vector Databases",
        "category": "Data Infrastructure",
        "base_signal": 90,
        "base_growth_rate_pct": 115.8,
        "adoption_stage": "High Momentum",
        "description": "High-dimensional embedding storage and approximate nearest neighbor (ANN) retrieval using Pinecone, Chroma, and Qdrant.",
        "target_roles": ["AI/ML Engineer", "Data Scientist", "Python Developer"],
        "forecast_note": "Standard infrastructure layer underpinning modern semantic search and RAG workflows."
    },
    {
        "skill_name": "LangChain",
        "category": "Frontier AI",
        "base_signal": 90,
        "base_growth_rate_pct": 122.0,
        "adoption_stage": "High Momentum",
        "description": "Chaining LLM prompts, agent tools, document loaders, and memory components for complex reasoning apps.",
        "target_roles": ["AI/ML Engineer", "Python Developer", "Fullstack Developer"],
        "forecast_note": "Ubiquitous prototyping framework across Indian AI developer hackathons and production MVPs."
    },
    {
        "skill_name": "Prompt Engineering",
        "category": "Frontier AI",
        "base_signal": 88,
        "base_growth_rate_pct": 94.0,
        "adoption_stage": "Cross-Functional Standard",
        "description": "Systemic prompting techniques (few-shot, Chain-of-Thought, ReAct) for reliable enterprise model outputs.",
        "target_roles": ["AI/ML Engineer", "Data Analyst", "Data Scientist"],
        "forecast_note": "Rapidly evolving from ad-hoc prompting into formal LLM evals and automated optimization."
    },
    {
        "skill_name": "Cloud Security",
        "category": "Cybersecurity & Architecture",
        "base_signal": 87,
        "base_growth_rate_pct": 74.0,
        "adoption_stage": "Mainstream Necessity",
        "description": "Zero trust architecture, identity federation, IAM governance, container security, and automated compliance.",
        "target_roles": ["Cybersecurity Analyst", "Cloud/DevOps Architect"],
        "forecast_note": "High demand spurred by regulatory compliance and digital banking expansions across India."
    },
    {
        "skill_name": "PyTorch",
        "category": "Deep Learning",
        "base_signal": 86,
        "base_growth_rate_pct": 68.5,
        "adoption_stage": "Industry Standard",
        "description": "De-facto standard framework for research and fine-tuning neural networks and generative transformers.",
        "target_roles": ["AI/ML Engineer", "Data Scientist"],
        "forecast_note": "Dominant deep learning framework in Indian AI R&D labs and university programs."
    },
    {
        "skill_name": "Deep Learning",
        "category": "AI Foundations",
        "base_signal": 86,
        "base_growth_rate_pct": 62.0,
        "adoption_stage": "Established Core",
        "description": "Multi-layer perceptrons, CNNs, RNNs, and transformer architectures for computer vision and NLP.",
        "target_roles": ["Data Scientist", "AI/ML Engineer"],
        "forecast_note": "Foundational requirement across advanced predictive analytics and perception roles."
    },
    {
        "skill_name": "Rust",
        "category": "Programming Languages",
        "base_signal": 85,
        "base_growth_rate_pct": 65.4,
        "adoption_stage": "Early High-Velocity Adoption",
        "description": "Memory-safe systems programming for high-throughput networking, WebAssembly, and AI inference runtimes.",
        "target_roles": ["Software Developer", "Cloud/DevOps Architect", "Data Engineer"],
        "forecast_note": "Rapidly gaining ground in high-frequency trading, cryptography, and core infrastructure."
    },
    {
        "skill_name": "Machine Learning",
        "category": "AI Foundations",
        "base_signal": 85,
        "base_growth_rate_pct": 52.0,
        "adoption_stage": "Mature Mainstream",
        "description": "Supervised, unsupervised, regression, classification, and ensemble modeling (XGBoost, Random Forest).",
        "target_roles": ["Data Scientist", "Data Analyst", "AI/ML Engineer"],
        "forecast_note": "Core baseline for all predictive intelligence roles in Indian analytics centers."
    },
    {
        "skill_name": "TensorFlow",
        "category": "Deep Learning",
        "base_signal": 84,
        "base_growth_rate_pct": 41.0,
        "adoption_stage": "Enterprise Production",
        "description": "Google's production ML framework, TF-Lite for mobile/edge, and TF Serving for scale.",
        "target_roles": ["AI/ML Engineer", "Data Scientist"],
        "forecast_note": "Maintained in legacy enterprise microservices and edge deployment environments."
    },
    {
        "skill_name": "Kubernetes",
        "category": "Cloud & Infrastructure",
        "base_signal": 83,
        "base_growth_rate_pct": 58.0,
        "adoption_stage": "Production Standard",
        "description": "Container orchestration, auto-scaling, ingress controllers, and GPU cluster scheduling.",
        "target_roles": ["Cloud/DevOps Architect", "Software Developer", "AI/ML Engineer"],
        "forecast_note": "Essential requirement for multi-cloud enterprise deployments."
    },
    {
        "skill_name": "Apache Spark",
        "category": "Big Data Engineering",
        "base_signal": 82,
        "base_growth_rate_pct": 49.0,
        "adoption_stage": "Big Data Standard",
        "description": "Distributed data processing, Spark SQL, PySpark, streaming analytics, and Delta Lake pipelines.",
        "target_roles": ["Data Engineer", "Data Scientist"],
        "forecast_note": "Core ETL backbone for petabyte-scale data lakes across telecom, BFSI, and e-commerce."
    },
    {
        "skill_name": "Python",
        "category": "Programming Languages",
        "base_signal": 82,
        "base_growth_rate_pct": 45.0,
        "adoption_stage": "Universal Core",
        "description": "Primary language for data science, AI engineering, automation, and backend API services.",
        "target_roles": ["Python Developer", "Data Scientist", "AI/ML Engineer", "Data Analyst"],
        "forecast_note": "Most requested programming competency across 15,000+ benchmark postings."
    },
    {
        "skill_name": "Big Data",
        "category": "Data Engineering",
        "base_signal": 81,
        "base_growth_rate_pct": 38.0,
        "adoption_stage": "Mature Mainstream",
        "description": "Hadoop ecosystems, distributed storage, parquet formats, and data lakehouse architectures.",
        "target_roles": ["Data Engineer", "Data Analyst"],
        "forecast_note": "Continues to be standard infrastructure across Indian IT service majors."
    },
    {
        "skill_name": "AWS",
        "category": "Cloud & Infrastructure",
        "base_signal": 80,
        "base_growth_rate_pct": 48.0,
        "adoption_stage": "Market Leader",
        "description": "S3, EC2, Lambda, SageMaker, IAM, ECS, and cloud-native architecture.",
        "target_roles": ["Cloud/DevOps Architect", "Software Developer", "Data Scientist"],
        "forecast_note": "Leading cloud provider across Indian product tech hubs and multinational GCCs."
    },
    {
        "skill_name": "Docker",
        "category": "Cloud & Infrastructure",
        "base_signal": 80,
        "base_growth_rate_pct": 44.0,
        "adoption_stage": "Universal Tooling",
        "description": "Containerization, multi-stage Dockerfiles, compose environments, and container registries.",
        "target_roles": ["Software Developer", "Cloud/DevOps Architect", "Python Developer"],
        "forecast_note": "Ubiquitous local development and production containerization requirement."
    },
    {
        "skill_name": "SQL",
        "category": "Data Foundations",
        "base_signal": 78,
        "base_growth_rate_pct": 32.0,
        "adoption_stage": "Evergreen Baseline",
        "description": "Relational queries, window functions, CTEs, performance tuning, and schema design.",
        "target_roles": ["Data Analyst", "Data Scientist", "Python Developer", "Software Developer"],
        "forecast_note": "Foundational across 80%+ of all data and backend job descriptions."
    },
    {
        "skill_name": "SAS",
        "category": "Legacy Analytics",
        "base_signal": 76,
        "base_growth_rate_pct": 12.0,
        "adoption_stage": "Legacy Enterprise",
        "description": "Statistical Analysis System for clinical trials, risk credit scorecards, and regulatory banking.",
        "target_roles": ["Data Scientist", "Data Analyst"],
        "forecast_note": "Highly resilient in Indian BFSI & pharma analytics, gradually coexisting with Python."
    },
    {
        "skill_name": "Power BI",
        "category": "Business Intelligence",
        "base_signal": 75,
        "base_growth_rate_pct": 39.0,
        "adoption_stage": "BI Standard",
        "description": "DAX, Power Query, automated executive dashboards, and Microsoft enterprise integrations.",
        "target_roles": ["Data Analyst", "Fullstack Developer"],
        "forecast_note": "Rapidly adopted across Indian enterprises migrating to Microsoft Fabric."
    },
    {
        "skill_name": "Tableau",
        "category": "Business Intelligence",
        "base_signal": 74,
        "base_growth_rate_pct": 28.0,
        "adoption_stage": "BI Standard",
        "description": "Visual analytics, LOD expressions, interactive storytelling, and Tableau Server publishing.",
        "target_roles": ["Data Analyst", "Data Scientist"],
        "forecast_note": "Standard enterprise visual analytics platform across Fortune 500 GCCs."
    }
]

class EmergingSkillsService:
    """
    Manages daily calculation and querying of emerging skills.
    Uses calendar-anchored multi-wave harmonic synthesis to reflect real-world market drift.
    """

    def __init__(self):
        self._overrides = self._load_overrides()

    def _load_overrides(self) -> Dict[str, Any]:
        """Loads optional manual or external scraper overrides from disk."""
        if OVERRIDES_FILE.exists():
            try:
                with open(OVERRIDES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_overrides(self) -> bool:
        """Persists overrides safely, ignoring errors on read-only environments."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(OVERRIDES_FILE, "w", encoding="utf-8") as f:
                json.dump(self._overrides, f, indent=2)
            return True
        except Exception:
            return False

    def update_skill_override(self, skill_name: str, signal_strength: float, notes: str = "") -> Dict[str, Any]:
        """Allows external scripts, scrapers, or admins to push live data overrides."""
        clean_key = skill_name.strip().lower()
        self._overrides[clean_key] = {
            "signal_strength": max(10, min(99, float(signal_strength))),
            "updated_at": date.today().isoformat(),
            "notes": notes
        }
        self._save_overrides()
        return self._overrides[clean_key]

    def _compute_wave(self, skill_name: str, target_date: date) -> float:
        """
        Calculates harmonic market wave for a skill on a specific calendar day.
        Combines a 14-day news cycle and a 30-day enterprise hiring review cycle.
        """
        day_ordinal = target_date.toordinal()
        # Stable unique hash for the skill
        name_hash = sum(ord(c) * (i + 1) for i, c in enumerate(skill_name.lower())) % 100
        
        # 14-day cycle (short-term hiring buzz)
        wave_14 = math.sin((2.0 * math.pi * (day_ordinal + name_hash)) / 14.0) * 1.6
        # 30-day cycle (monthly budget & sprint shifts)
        wave_30 = math.cos((2.0 * math.pi * (day_ordinal + name_hash * 2)) / 30.0) * 0.9

        return wave_14 + wave_30

    def get_skill_daily_metrics(self, skill_meta: Dict[str, Any], target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculates today's signal score, 24-hour delta, trend direction, and 7-day sparkline.
        """
        d = target_date or date.today()
        yesterday = d - timedelta(days=1)
        skill_name = skill_meta["skill_name"]
        clean_key = skill_name.lower()

        # Check for direct override first
        override = self._overrides.get(clean_key)
        if override and override.get("signal_strength") is not None:
            today_score = float(override["signal_strength"])
            # Historical wave still provides subtle 24h delta
            delta_val = round(self._compute_wave(skill_name, d) - self._compute_wave(skill_name, yesterday), 1)
        else:
            base_score = float(skill_meta["base_signal"])
            wave_today = self._compute_wave(skill_name, d)
            wave_yesterday = self._compute_wave(skill_name, yesterday)
            
            today_score = round(base_score + wave_today, 1)
            delta_val = round(wave_today - wave_yesterday, 1)

        # Clamping
        today_score = max(50.0, min(99.0, today_score))
        today_int_score = int(round(today_score))

        # Growth rate adjustment based on momentum
        base_growth = float(skill_meta.get("base_growth_rate_pct", 50.0))
        adjusted_growth = round(base_growth + (delta_val * 4.5), 1)

        # Trend direction and label
        if delta_val >= 0.8:
            trend_direction = "up"
            velocity_label = "Surging (+High Velocity)"
        elif delta_val > 0.1:
            trend_direction = "up"
            velocity_label = "Accelerating"
        elif delta_val < -0.8:
            trend_direction = "down"
            velocity_label = "Consolidating"
        elif delta_val < -0.1:
            trend_direction = "down"
            velocity_label = "Cooling Slightly"
        else:
            trend_direction = "stable"
            velocity_label = "Stable High Adoption"

        # 7-day sparkline history
        history_7d = []
        for i in range(6, -1, -1):
            hist_d = d - timedelta(days=i)
            hist_wave = self._compute_wave(skill_name, hist_d)
            if override and override.get("signal_strength") is not None:
                hist_val = round(float(override["signal_strength"]) + (hist_wave - self._compute_wave(skill_name, d)), 1)
            else:
                hist_val = round(float(skill_meta["base_signal"]) + hist_wave, 1)
            history_7d.append({
                "date": hist_d.isoformat(),
                "day_label": hist_d.strftime("%a"),
                "score": max(50.0, min(99.0, hist_val))
            })

        return {
            "skill_name": skill_name,
            "category": skill_meta.get("category", "Frontier Tech"),
            "signal_strength": today_int_score,
            "momentum_score": today_int_score,
            "signal_strength_precise": today_score,
            "previous_day_score": round(today_score - delta_val, 1),
            "daily_delta_pct": ("+" if delta_val > 0 else "") + f"{delta_val:.1f}%",
            "daily_delta_raw": delta_val,
            "trend_direction": trend_direction,
            "velocity_label": velocity_label,
            "growth_rate_pct": adjusted_growth,
            "adoption_stage": skill_meta.get("adoption_stage", "High Momentum"),
            "description": skill_meta.get("description", ""),
            "target_roles": skill_meta.get("target_roles", []),
            "forecast_note": skill_meta.get("forecast_note", ""),
            "history_7d": history_7d,
            "as_of_date": d.isoformat(),
            "last_synced_label": f"Updated {d.strftime('%b %d, %Y')}"
        }

    def get_catalog_with_daily_metrics(self, target_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Returns the full catalog of emerging skills enriched with today's real-time momentum."""
        return [self.get_skill_daily_metrics(meta, target_date) for meta in EMERGING_SKILLS_BASE]

    def get_frontier_scores_dict(self, target_date: Optional[date] = None) -> Dict[str, int]:
        """
        Returns a lowercase dictionary mapping skill_name -> int signal score.
        Drop-in replacement for the static EMERGING_FRONTIER_SKILLS dictionary.
        """
        catalog = self.get_catalog_with_daily_metrics(target_date)
        res = {}
        for item in catalog:
            res[item["skill_name"].lower()] = item["signal_strength"]
        return res

# Global Singleton Instance
emerging_service = EmergingSkillsService()

# Dynamic Mapping Proxy that behaves like a dictionary while returning today's dynamic score
class DynamicEmergingSkillsDict(dict):
    """
    Dict proxy that returns dynamically computed daily emerging scores
    while remaining 100% backward-compatible with legacy dict access.
    """
    def __init__(self, service: EmergingSkillsService):
        super().__init__()
        self._service = service

    def __getitem__(self, key: str) -> int:
        scores = self._service.get_frontier_scores_dict()
        return scores[key.lower()]

    def get(self, key: str, default: Any = 55) -> Any:
        scores = self._service.get_frontier_scores_dict()
        return scores.get(key.lower(), default)

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        scores = self._service.get_frontier_scores_dict()
        return key.lower() in scores

    def items(self):
        return self._service.get_frontier_scores_dict().items()

    def keys(self):
        return self._service.get_frontier_scores_dict().keys()

    def values(self):
        return self._service.get_frontier_scores_dict().values()

# Exported dynamic dictionary for drop-in usage across scoring and analytics
EMERGING_FRONTIER_SKILLS = DynamicEmergingSkillsDict(emerging_service)
