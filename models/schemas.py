"""
Pydantic Schemas for SkillPulse Bharat
Team: Syntax Society
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class JobPosting(BaseModel):
    id: Optional[int] = None
    job_title: str
    company: str
    industry: str
    location: str
    date: str
    skills: List[str]
    experience_years: int = 2
    salary_lpa: Optional[float] = None
    description: Optional[str] = None

class RelatedSkill(BaseModel):
    skill: str
    correlation: float
    co_occurrences: int

class SkillStats(BaseModel):
    skill_name: str
    category: str
    total_jobs: int
    demand_percentage: float
    demand_score: int  # 0 to 100
    momentum: str  # "Rapidly Growing", "Steady Growth", "High Demand", "Stable", "Declining"
    qoq_growth: float  # e.g., +24.5%
    top_industries: List[Dict[str, Any]]
    related_skills: List[RelatedSkill]

class SkillTrendPoint(BaseModel):
    quarter: str
    count: int
    is_forecast: bool
    confidence_low: Optional[int] = None
    confidence_high: Optional[int] = None

class SkillTrendResponse(BaseModel):
    skill_name: str
    historical_points: List[SkillTrendPoint]
    forecast_points: List[SkillTrendPoint]
    cagr_projection: float
    verdict: str
    disclaimer: str = "Forecast is a statistical projection based on quarterly CAGR momentum and not an absolute guarantee."

class RoleAnalysisResponse(BaseModel):
    role_name: str
    description: str
    total_jobs: int
    avg_salary_lpa: float
    core_skills: List[Dict[str, Any]]
    complementary_skills: List[Dict[str, Any]]
    emerging_skills: List[str]
    industry_spread: List[Dict[str, Any]]
    location_spread: List[Dict[str, Any]]

class EmergingSkillItem(BaseModel):
    skill_name: str
    category: str
    growth_rate_pct: float
    momentum_score: int
    adoption_stage: str  # "Frontier", "Early Adoption", "High Momentum", "Mainstream Shift"
    description: str
    target_roles: List[str]
    forecast_note: str

class RecommendationRequest(BaseModel):
    target_role: str
    user_skills: List[str]
    experience_level: Optional[str] = "Student/Fresher"

class LearningStep(BaseModel):
    step_number: int
    skill: str
    importance: str  # "Critical Core", "High-Impact", "Emerging Edge"
    why_needed: str
    estimated_weeks: int
    recommended_resources: List[str]

class RecommendationResponse(BaseModel):
    target_role: str
    match_percentage: float
    matched_skills: List[str]
    missing_core_skills: List[str]
    missing_complementary_skills: List[str]
    recommended_next_skills: List[str]
    learning_roadmap: List[LearningStep]
    skill_gap_summary: Dict[str, Any]

class ExtractRequest(BaseModel):
    text: str

class ExtractResponse(BaseModel):
    extracted_skills: List[str]
    raw_detected_count: int
    matched_canonical_skills: List[str]
    top_matching_roles: List[Dict[str, Any]]
    processing_time_ms: float

class JobMatchRequest(BaseModel):
    resume_text: Optional[str] = ""
    skills: Optional[List[str]] = None
    target_role: Optional[str] = None
    location: Optional[str] = None
    min_score: Optional[float] = 30.0
    max_experience: Optional[int] = None
    limit: Optional[int] = 20

class JobOpeningCard(BaseModel):
    id: Optional[int] = None
    job_title: str
    company: str
    industry: str
    location: str
    date: str
    quarter: Optional[str] = ""
    experience_years: int
    experience_label: str
    salary_lpa: float
    salary_display: str
    match_score: float
    match_tier: str
    skill_coverage_pct: float
    matched_skills: List[str]
    missing_skills: List[str]
    total_required_skills: int
    skills_match_ratio: str
    description: str
    links: Dict[str, str]

class CandidateMatchProfile(BaseModel):
    extracted_skills: List[str]
    raw_count: int
    estimated_experience_years: int
    experience_tier: str
    top_predicted_roles: List[Dict[str, Any]]

class JobMatchResponse(BaseModel):
    candidate_profile: CandidateMatchProfile
    total_jobs_searched: int
    matched_count: int
    jobs: List[JobOpeningCard]
