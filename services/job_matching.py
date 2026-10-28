"""
Resume-Job Matching AI Engine for AROHA
Team: Syntax Society

Provides deep ML/NLP matching between uploaded candidate resumes and real/benchmark
job market openings, calculating multi-factor compatibility scores and generating
live direct application and search links (LinkedIn, Naukri, Google Jobs).
"""

import re
import math
import urllib.parse
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set

from backend import database
from services.skill_extractor import extractor
from utils.normalizer import normalize_skill, CANONICAL_SKILLS
from utils.constants import ROLE_SKILL_PROFILES, TARGET_ROLES

# Optional scikit-learn import with fallback
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def generate_job_links(job_title: str, company: str, location: str) -> Dict[str, str]:
    """
    Constructs live, high-intent job application and search URLs across major portals.
    """
    role_company = f"{job_title} {company}"
    enc_rc = urllib.parse.quote(role_company)
    enc_role = urllib.parse.quote(job_title)
    enc_company = urllib.parse.quote(company)
    enc_loc = urllib.parse.quote(location)

    # Clean slugs for portal paths
    role_slug = re.sub(r'[^a-zA-Z0-9]+', '-', job_title.lower()).strip('-')
    loc_slug = re.sub(r'[^a-zA-Z0-9]+', '-', location.split(',')[0].strip().lower()).strip('-')

    linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={enc_rc}&location={enc_loc}"
    google_jobs_url = f"https://www.google.com/search?q={urllib.parse.quote(f'{company} {job_title} jobs in {location} apply')}"
    naukri_url = f"https://www.naukri.com/{role_slug}-jobs-in-{loc_slug}?k={enc_role}"
    indeed_url = f"https://in.indeed.com/jobs?q={enc_rc}&l={enc_loc}"
    company_careers_url = f"https://www.google.com/search?q={urllib.parse.quote(f'{company} careers {job_title}')}"

    return {
        "apply_url": linkedin_url,
        "linkedin_url": linkedin_url,
        "naukri_url": naukri_url,
        "google_jobs_url": google_jobs_url,
        "indeed_url": indeed_url,
        "company_careers_url": company_careers_url
    }


def estimate_experience_from_text(text: str) -> Tuple[int, str]:
    """
    Estimates candidate's experience years and seniority tier from resume text.
    Returns (years, tier_name).
    """
    if not text:
        return 1, "Fresher / Entry (0-1 yrs)"

    lower_text = text.lower()

    # Look for explicit patterns like '5+ years of experience', '3 yrs exp'
    exp_patterns = [
        r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s*of)?\s*(?:relevant\s*)?(?:hands-on\s*)?(?:experience|exp)',
        r'(?:total|overall|relevant)?\s*experience\s*[:\-–]\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)',
        r'experience\s*of\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)'
    ]
    detected_years: List[float] = []
    for pat in exp_patterns:
        for m in re.finditer(pat, lower_text):
            try:
                val = float(m.group(1))
                if 0 <= val <= 35:
                    detected_years.append(val)
            except ValueError:
                continue

    # Look for employment date spans: e.g. 2018 - 2024
    year_spans = re.findall(r'\b(20\d\d)\s*[-–—to]\s*(?:present|current|now|(20\d\d))\b', lower_text)
    span_years = 0
    current_year = 2025
    for start_yr, end_yr in year_spans:
        try:
            start = int(start_yr)
            end = int(end_yr) if end_yr else current_year
            if 1990 <= start <= end <= current_year:
                span_years = max(span_years, end - start)
        except ValueError:
            pass

    if span_years > 0:
        detected_years.append(float(span_years))

    if detected_years:
        max_exp = int(round(max(detected_years)))
    else:
        # Check seniority keywords
        if any(w in lower_text for w in ["principal", "lead architect", "director", "head of", "vp "]):
            max_exp = 9
        elif any(w in lower_text for w in ["senior data scientist", "senior engineer", "senior developer", "sr. "]):
            max_exp = 5
        elif any(w in lower_text for w in ["intern", "student", "graduate", "fresher", "entry level", "b.tech student"]):
            max_exp = 0
        else:
            max_exp = 2

    if max_exp <= 1:
        tier = "Fresher / Entry (0-1 yrs)"
    elif max_exp <= 3:
        tier = "Junior (1-3 yrs)"
    elif max_exp <= 6:
        tier = "Mid-Level (3-6 yrs)"
    elif max_exp <= 9:
        tier = "Senior (6-9 yrs)"
    else:
        tier = "Lead / Principal (10+ yrs)"

    return max_exp, tier


class ResumeJobMatcher:
    """
    AI Matching Model linking candidate resumes to real/benchmark job openings.
    Combines:
    - Skill Set Overlap & Coverage (45%)
    - Semantic / TF-IDF Vector Cosine Similarity (30%)
    - Role & Domain Alignment (15%)
    - Experience Fit (10%)
    """

    def __init__(self):
        self._cached_jobs: Optional[List[Dict[str, Any]]] = None
        self._tfidf_vectorizer = None
        self._job_vectors = None
        self._job_texts: List[str] = []

    def _ensure_jobs_loaded(self) -> List[Dict[str, Any]]:
        """Loads jobs from database with memory caching for fast queries."""
        if self._cached_jobs is None or len(self._cached_jobs) == 0:
            jobs = database.get_all_jobs_with_skills()
            if not jobs:
                # Fallback to json if DB not yet queried
                from utils.constants import INDIAN_LOCATIONS, TOP_COMPANIES
                import json
                json_path = Path(__file__).resolve().parent.parent / "data" / "sample_jobs.json"
                if json_path.exists():
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            jobs = json.load(f)
                    except Exception:
                        jobs = []
            self._cached_jobs = jobs
            self._build_vector_index()
        return self._cached_jobs

    def _build_vector_index(self):
        """Builds TF-IDF vector index across all job texts for rapid semantic matching."""
        if not self._cached_jobs:
            return

        self._job_texts = []
        for j in self._cached_jobs:
            skills_str = " ".join(j.get("skills", []))
            title = j.get("job_title", "")
            desc = j.get("description", "")
            ind = j.get("industry", "")
            full_text = f"{title} {title} {skills_str} {skills_str} {desc} {ind}"
            self._job_texts.append(full_text)

        if SKLEARN_AVAILABLE and len(self._job_texts) > 0:
            try:
                self._tfidf_vectorizer = TfidfVectorizer(
                    ngram_range=(1, 2),
                    max_features=4000,
                    stop_words="english"
                )
                self._job_vectors = self._tfidf_vectorizer.fit_transform(self._job_texts)
            except Exception:
                self._tfidf_vectorizer = None
                self._job_vectors = None

    def extract_resume_text(self, contents: bytes, filename: str) -> str:
        """Extracts clean text from PDF, DOCX, or TXT file contents in memory."""
        ext = Path(filename).suffix.lower()
        if ext == ".txt":
            return contents.decode("utf-8", errors="ignore")
        elif ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(contents))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext in [".docx", ".doc"]:
            from docx import Document
            document = Document(BytesIO(contents))
            return "\n".join(p.text for p in document.paragraphs)
        else:
            return contents.decode("utf-8", errors="ignore")

    def profile_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Extracts skills, estimated experience, and role alignment from resume text.
        """
        extracted = extractor.extract_skills(resume_text)
        exp_years, exp_tier = estimate_experience_from_text(resume_text)

        return {
            "extracted_skills": extracted["extracted_skills"],
            "raw_count": extracted["raw_count"],
            "estimated_experience_years": exp_years,
            "experience_tier": exp_tier,
            "top_predicted_roles": extracted["role_alignments"][:4],
            "processing_time_ms": extracted["processing_time_ms"]
        }

    def _compute_semantic_similarities(self, resume_text: str) -> List[float]:
        """Calculates cosine similarity between resume and each job posting."""
        jobs_count = len(self._cached_jobs or [])
        if jobs_count == 0:
            return []

        if SKLEARN_AVAILABLE and self._tfidf_vectorizer is not None and self._job_vectors is not None:
            try:
                resume_vec = self._tfidf_vectorizer.transform([resume_text])
                sims = cosine_similarity(resume_vec, self._job_vectors)[0]
                return [float(s) for s in sims]
            except Exception:
                pass

        # Pure Python fallback: token overlap cosine approximation
        resume_tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower()))
        sims = []
        for text in self._job_texts:
            job_tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()))
            if not job_tokens or not resume_tokens:
                sims.append(0.0)
            else:
                inter = len(resume_tokens.intersection(job_tokens))
                denom = math.sqrt(len(resume_tokens) * len(job_tokens))
                sims.append(round(inter / denom, 4) if denom > 0 else 0.0)
        return sims

    def match_resume(
        self,
        resume_text: str,
        user_skills: Optional[List[str]] = None,
        target_role: Optional[str] = None,
        location_filter: Optional[str] = None,
        min_score: float = 35.0,
        max_experience: Optional[int] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Matches a resume text against all indexed job openings using hybrid multi-factor scoring.
        """
        jobs = self._ensure_jobs_loaded()
        if not jobs:
            return {
                "candidate_profile": {
                    "extracted_skills": [],
                    "raw_count": 0,
                    "estimated_experience_years": 0,
                    "experience_tier": "Entry",
                    "top_predicted_roles": []
                },
                "total_jobs_searched": 0,
                "matched_count": 0,
                "jobs": []
            }

        # 1. Profile Candidate Resume
        profile = self.profile_resume(resume_text)
        cand_skills = set(profile["extracted_skills"])
        if user_skills:
            for s in user_skills:
                norm = normalize_skill(s)
                cand_skills.add(norm if norm else s.strip())

        cand_skills_list = sorted(list(cand_skills))
        cand_exp = profile["estimated_experience_years"]
        top_roles = [r["role"] for r in profile["top_predicted_roles"]]

        # 2. Semantic Similarities
        semantic_sims = self._compute_semantic_similarities(resume_text)

        matched_results: List[Dict[str, Any]] = []

        for idx, job in enumerate(jobs):
            # Check location filter
            if location_filter and location_filter.lower() not in ["all", "any", ""]:
                if location_filter.lower() not in job.get("location", "").lower():
                    continue

            # Check role filter
            if target_role and target_role.lower() not in ["all", "any", ""]:
                if target_role.lower() not in job.get("job_title", "").lower():
                    continue

            # Check max experience filter
            job_exp = job.get("experience_years", 2)
            if max_experience is not None and job_exp > max_experience:
                continue

            job_skills = set(job.get("skills", []))
            matched_skills = sorted(list(cand_skills.intersection(job_skills)))
            missing_skills = sorted(list(job_skills - cand_skills))

            # Factor 1: Skill Coverage (0.0 to 1.0)
            if job_skills:
                skill_cov = len(matched_skills) / len(job_skills)
            else:
                skill_cov = 0.5
            # Small bonus if candidate has complementary skills beyond the core
            extra_skills_count = len(cand_skills - job_skills)
            skill_score = min(1.0, skill_cov + (min(extra_skills_count, 5) * 0.02))

            # Factor 2: Semantic Similarity (0.0 to 1.0)
            sem_sim = semantic_sims[idx] if idx < len(semantic_sims) else 0.0

            # Factor 3: Role / Title Alignment (0.0 to 1.0)
            job_title = job.get("job_title", "")
            if top_roles and job_title == top_roles[0]:
                role_score = 1.0
            elif job_title in top_roles:
                role_score = 0.8
            else:
                role_score = 0.35

            # Factor 4: Experience Alignment (0.0 to 1.0)
            exp_diff = job_exp - cand_exp
            if exp_diff <= 0:
                # Candidate has equal or more experience
                exp_score = 1.0
            elif exp_diff == 1:
                exp_score = 0.85
            elif exp_diff == 2:
                exp_score = 0.65
            elif exp_diff == 3:
                exp_score = 0.45
            else:
                exp_score = max(0.15, 1.0 - (exp_diff * 0.2))

            # Composite Multi-Factor Score:
            # 45% Skills + 30% Semantic + 15% Role + 10% Experience
            composite = (
                (0.45 * skill_score) +
                (0.30 * sem_sim) +
                (0.15 * role_score) +
                (0.10 * exp_score)
            )

            # Boost if exact core skills matched strongly
            if len(matched_skills) >= 4 and skill_cov >= 0.7:
                composite = min(1.0, composite * 1.15)

            final_score_pct = round(min(99.4, max(12.0, composite * 100)), 1)

            if final_score_pct < min_score:
                continue

            # Determine Tier
            if final_score_pct >= 85.0:
                match_tier = "Top Match"
            elif final_score_pct >= 70.0:
                match_tier = "Strong Match"
            elif final_score_pct >= 50.0:
                match_tier = "Good Match"
            else:
                match_tier = "Potential Fit"

            # Construct verified direct links
            links = generate_job_links(
                job_title=job_title,
                company=job.get("company", "Tech Company"),
                location=job.get("location", "India")
            )

            matched_results.append({
                "id": job.get("id"),
                "job_title": job_title,
                "company": job.get("company", "Tech Company"),
                "industry": job.get("industry", "Technology"),
                "location": job.get("location", "India"),
                "date": job.get("date", "Recent"),
                "quarter": job.get("quarter", ""),
                "experience_years": job_exp,
                "experience_label": f"{job_exp}+ yrs" if job_exp > 0 else "Fresher (0 yrs)",
                "salary_lpa": job.get("salary_lpa", 8.0),
                "salary_display": f"₹{job.get('salary_lpa', 8.0)} LPA",
                "match_score": final_score_pct,
                "match_tier": match_tier,
                "skill_coverage_pct": round(skill_cov * 100, 1),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "total_required_skills": len(job_skills),
                "skills_match_ratio": f"{len(matched_skills)} of {len(job_skills)} matched",
                "description": job.get("description", ""),
                "links": links
            })

        # Sort descending by match score
        matched_results.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "candidate_profile": {
                "extracted_skills": cand_skills_list,
                "raw_count": len(cand_skills_list),
                "estimated_experience_years": cand_exp,
                "experience_tier": profile["experience_tier"],
                "top_predicted_roles": profile["top_predicted_roles"]
            },
            "total_jobs_searched": len(jobs),
            "matched_count": len(matched_results),
            "jobs": matched_results[:limit]
        }


# Global singleton instance
job_matcher = ResumeJobMatcher()
