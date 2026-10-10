"""
Unit tests for JDS and SDS Machine Learning Models
Team: Syntax Society
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.success_models import success_service
from services.data_service import data_service
from services.data_service import parse_salary_bracket, parse_lpa_string

def test_salary_parsing():
    assert parse_salary_bracket("6to10") == 8.0
    assert parse_salary_bracket("10to15") == 12.5
    assert parse_salary_bracket("0to3") == 1.5
    assert parse_salary_bracket("25to50") == 37.5

    assert parse_lpa_string("7.8L") == 7.8
    assert parse_lpa_string("16.0L") == 16.0
    assert parse_lpa_string("4.5l") == 4.5

def test_jds_model_training_and_prediction():
    for model_type in ["logistic_regression", "random_forest"]:
        res = success_service.predict_jds_salary_hike(
            big_data=4.0,
            maths_stats=4.5,
            coding=4.2,
            ai_ml=4.8,
            dashboard=3.5,
            model_type=model_type
        )
        assert "high_hike_probability_pct" in res
        assert 0.0 <= res["high_hike_probability_pct"] <= 100.0
        assert "evaluation_metrics" in res
        metrics = res["evaluation_metrics"]
        assert metrics["accuracy"] >= 0.75, f"Expected accuracy >= 0.75, got {metrics['accuracy']}"
        assert metrics["precision"] >= 0.75, f"Expected precision >= 0.75, got {metrics['precision']}"
        assert metrics["recall"] >= 0.75, f"Expected recall >= 0.75, got {metrics['recall']}"
        assert metrics["f1"] >= 0.75, f"Expected f1 >= 0.75, got {metrics['f1']}"
        assert len(res["top_contributing_factors"]) == 5

def test_sds_model_training_and_prediction():
    for model_type in ["logistic_regression", "random_forest"]:
        res = success_service.predict_sds_success(
            neuroticism=30,
            extraversion=45,
            openness=52,
            agreeableness=48,
            conscientiousness=55,
            model_type=model_type
        )
        assert "success_probability_pct" in res
        assert 0.0 <= res["success_probability_pct"] <= 100.0
        assert "evaluation_metrics" in res
        metrics = res["evaluation_metrics"]
        assert metrics["accuracy"] >= 0.75, f"Expected accuracy >= 0.75, got {metrics['accuracy']}"
        assert metrics["precision"] >= 0.75, f"Expected precision >= 0.75, got {metrics['precision']}"
        assert metrics["recall"] >= 0.75, f"Expected recall >= 0.75, got {metrics['recall']}"
        assert metrics["f1"] >= 0.75, f"Expected f1 >= 0.75, got {metrics['f1']}"
        assert len(res["top_contributing_factors"]) == 5

def test_data_quality_report():
    report = data_service.get_data_quality_report()
    assert report["analytics_jobs"]["rows"] == 15841
    assert report["datascience_jobs"]["rows"] == 1602
    assert report["jds_skill_traits"]["samples"] == 139
    assert report["sds_personality_traits"]["samples"] == 161

def test_model_accuracy_cross_validation():
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.dummy import DummyClassifier

    # 1. JDS Model CV Accuracy
    jds = data_service.get_jds_traits()
    X_jds = jds[["big_data_skills", "maths-stats_skills", "coding_skills", "ai_and_ml_skills", "dashboard_and_storytelling_skills"]]
    y_jds = jds["salary_hike_high_or_low"]

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    jds_lr_cv = cross_val_score(LogisticRegression(random_state=42), X_jds, y_jds, cv=cv, scoring="accuracy").mean()
    jds_dummy_cv = cross_val_score(DummyClassifier(strategy="most_frequent"), X_jds, y_jds, cv=cv, scoring="accuracy").mean()

    assert jds_lr_cv >= 0.80, f"Expected JDS CV accuracy >= 0.80, got {jds_lr_cv:.3f}"
    assert jds_lr_cv > jds_dummy_cv, "Model should significantly outperform dummy baseline"

    # 2. SDS Model CV Accuracy
    sds = data_service.get_sds_traits()
    X_sds = sds[["neuroticism", "extraversion", "openness_to_experience", "agreeableness", "conscientiousness"]]
    y_sds = sds["success_classification_high_low"]

    sds_lr_cv = cross_val_score(LogisticRegression(max_iter=1000, random_state=42), X_sds, y_sds, cv=cv, scoring="accuracy").mean()
    sds_rf_cv = cross_val_score(RandomForestClassifier(n_estimators=50, random_state=42), X_sds, y_sds, cv=cv, scoring="accuracy").mean()
    sds_dummy_cv = cross_val_score(DummyClassifier(strategy="most_frequent"), X_sds, y_sds, cv=cv, scoring="accuracy").mean()

    assert sds_lr_cv >= 0.85, f"Expected SDS LR CV accuracy >= 0.85, got {sds_lr_cv:.3f}"
    assert sds_rf_cv >= 0.90, f"Expected SDS RF CV accuracy >= 0.90, got {sds_rf_cv:.3f}"
    assert sds_rf_cv > sds_dummy_cv, "Model should significantly outperform dummy baseline"

