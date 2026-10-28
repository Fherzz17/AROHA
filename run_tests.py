"""
SkillPulse Bharat - Automated Test Runner
Team: Syntax Society
"""

import sys
import time
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests import test_skill_extractor
from tests import test_analytics
from tests import test_recommender
from tests import test_api
from tests import test_sas_models
from tests import test_scoring
from tests import test_auth
from tests import test_job_matching

def run_all_tests():
    modules = [
        ("Skill Extraction & Normalizer", [
            ("User Requested Prompt Example", test_skill_extractor.test_user_requested_example),
            ("Alias Normalization", test_skill_extractor.test_normalization_aliases),
            ("Complex JD Extraction", test_skill_extractor.test_complex_job_description_extraction),
            ("Role Alignment Scoring", test_skill_extractor.test_role_alignment_scoring),
        ]),
        ("Predictive Machine Learning & Data Quality", [
            ("Salary Parsing Logic", test_sas_models.test_salary_parsing),
            ("JDS Career Advancement ML Model", test_sas_models.test_jds_model_training_and_prediction),
            ("SDS Personality Success ML Model", test_sas_models.test_sds_model_training_and_prediction),
            ("Data Quality Audit Report", test_sas_models.test_data_quality_report),
            ("Model Accuracy & Cross-Validation", test_sas_models.test_model_accuracy_cross_validation),
        ]),
        ("SkillPulse Score & Market Intelligence", [
            ("SkillPulse 4-Component Scoring", test_scoring.test_skillpulse_score_components),
            ("Market & Salary Intelligence Analytics", test_scoring.test_market_intelligence_services),
            ("Evidence-Based Recommendations", test_scoring.test_enhanced_recommendations),
            ("Daily Emerging Skills Engine", test_scoring.test_daily_emerging_skills_engine),
        ]),
        ("Database & Analytics Services", [
            ("Database Job & Skill Counts", test_analytics.test_database_counts),
            ("Dashboard KPI Aggregation", test_analytics.test_dashboard_summary),
            ("Individual Skill Profile", test_analytics.test_skill_profile),
            ("Observed vs Forecast Separation", test_analytics.test_observed_vs_forecast_separation),
        ]),
        ("Personalized Recommender", [
            ("Data Analyst Flow & Roadmap", test_recommender.test_data_analyst_recommendation_flow),
            ("Full Match Profile Case", test_recommender.test_perfect_match_case),
        ]),
        ("FastAPI Endpoints", [
            ("Health Check Endpoint", test_api.test_api_health),
            ("Dashboard Endpoint", test_api.test_api_dashboard),
            ("Skill Detail Endpoint", test_api.test_api_skill_detail),
            ("Role Detail Endpoint", test_api.test_api_role_detail),
            ("Emerging Skills Endpoint", test_api.test_api_emerging),
            ("Recommendation Endpoint", test_api.test_api_recommend),
            ("NLP Extraction Endpoint", test_api.test_api_extract),
        ]),
        ("User Authentication & Multi-Role Access", [
            ("Student Registration & Login", test_auth.test_auth_student_registration_and_login),
            ("Recruiter Registration & Login", test_auth.test_auth_recruiter_registration_and_login),
            ("Educator Registration", test_auth.test_auth_educator_registration),
            ("Duplicate Email Prevention", test_auth.test_auth_duplicate_email_prevention),
            ("Session Verification & Logout", test_auth.test_auth_session_me_and_logout),
            ("Social SSO OAuth Simulation", test_auth.test_auth_social_login),
        ]),
        ("AI Resume Job Matcher & Openings", [
            ("Experience Estimation & Seniority", test_job_matching.test_experience_estimation),
            ("Job Application & Search Links Generation", test_job_matching.test_job_links_generation),
            ("Resume Multi-Factor Scoring & Ranking", test_job_matching.test_resume_matching_scoring_and_ranking),
            ("Role & Location Filtering", test_job_matching.test_role_and_location_filters),
            ("API JSON Job Match Endpoint", test_job_matching.test_api_jobs_match_json_endpoint),
            ("API Resume Upload Job Match Endpoint", test_job_matching.test_api_jobs_match_resume_upload_endpoint),
            ("API Locations & Single Job Details", test_job_matching.test_api_jobs_locations_and_single_job),
        ])
    ]

    total_passed = 0
    total_failed = 0
    start_total = time.perf_counter()

    print("=" * 65)
    print("           AROHA - PRODUCT VERIFICATION TEST SUITE             ")
    print("=" * 65)

    for suite_name, test_cases in modules:
        print(f"\n[SUITE] {suite_name}")
        for test_name, test_fn in test_cases:
            try:
                test_fn()
                print(f"  [PASS] {test_name}")
                total_passed += 1
            except Exception as e:
                print(f"  [FAIL] {test_name} -> {e}")
                total_failed += 1

    duration = round((time.perf_counter() - start_total) * 1000, 2)
    print("\n" + "=" * 65)
    print(f"RESULTS: {total_passed} Passed | {total_failed} Failed | Execution Time: {duration} ms")
    print("=" * 65)

    if total_failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
