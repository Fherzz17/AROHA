"""
Career Success Intelligence & Machine Learning Models
Trains and evaluates interpretable predictive models on SAS datasets:
1. JDS Skill Traits: Technical competencies -> High Salary-Hike Likelihood
2. SDS Personality Traits: Big 5 personality traits -> Professional Success Profile

Team: Syntax Society
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from services.data_service import data_service

JDS_FEATURE_LABELS = {
    "big_data_skills": "Big Data (Hadoop, Spark, Distributed Systems)",
    "maths-stats_skills": "Maths & Statistics (Probability, Inference, Modeling)",
    "coding_skills": "Coding (Python, R, Algorithms, Clean Code)",
    "ai_and_ml_skills": "AI & ML (Supervised/Unsupervised, Deep Learning)",
    "dashboard_and_storytelling_skills": "Dashboard & Storytelling (Power BI, Tableau, Communication)"
}

SDS_FEATURE_LABELS = {
    "neuroticism": "Emotional Stability / Neuroticism (Stress reactivity)",
    "extraversion": "Extraversion (Social engagement & leadership)",
    "openness_to_experience": "Openness to Experience (Curiosity & innovation)",
    "agreeableness": "Agreeableness (Team collaboration & trust)",
    "conscientiousness": "Conscientiousness (Goal orientation & thoroughness)"
}

class SuccessModelService:
    def __init__(self):
        self._jds_models = None
        self._sds_models = None
        self._train_models()

    def _train_models(self):
        # 1. JDS Model
        jds = data_service.get_jds_traits()
        X_jds = jds[["big_data_skills", "maths-stats_skills", "coding_skills", "ai_and_ml_skills", "dashboard_and_storytelling_skills"]]
        y_jds = jds["salary_hike_high_or_low"]

        X_tr_j, X_te_j, y_tr_j, y_te_j = train_test_split(X_jds, y_jds, test_size=0.25, random_state=42, stratify=y_jds)

        lr_j = LogisticRegression().fit(X_tr_j, y_tr_j)
        rf_j = RandomForestClassifier(n_estimators=50, random_state=42).fit(X_tr_j, y_tr_j)

        y_p_lr_j = lr_j.predict(X_te_j)
        y_p_rf_j = rf_j.predict(X_te_j)

        self._jds_models = {
            "lr": lr_j,
            "rf": rf_j,
            "features": list(X_jds.columns),
            "sample_size": len(jds),
            "metrics": {
                "logistic_regression": {
                    "accuracy": round(accuracy_score(y_te_j, y_p_lr_j), 3),
                    "precision": round(precision_score(y_te_j, y_p_lr_j), 3),
                    "recall": round(recall_score(y_te_j, y_p_lr_j), 3),
                    "f1": round(f1_score(y_te_j, y_p_lr_j), 3),
                    "confusion_matrix": confusion_matrix(y_te_j, y_p_lr_j).tolist(),
                    "coefficients": dict(zip(X_jds.columns, lr_j.coef_[0].round(3)))
                },
                "random_forest": {
                    "accuracy": round(accuracy_score(y_te_j, y_p_rf_j), 3),
                    "precision": round(precision_score(y_te_j, y_p_rf_j), 3),
                    "recall": round(recall_score(y_te_j, y_p_rf_j), 3),
                    "f1": round(f1_score(y_te_j, y_p_rf_j), 3),
                    "confusion_matrix": confusion_matrix(y_te_j, y_p_rf_j).tolist(),
                    "importances": dict(zip(X_jds.columns, rf_j.feature_importances_.round(3)))
                }
            }
        }

        # 2. SDS Model
        sds = data_service.get_sds_traits()
        X_sds = sds[["neuroticism", "extraversion", "openness_to_experience", "agreeableness", "conscientiousness"]]
        y_sds = sds["success_classification_high_low"]

        X_tr_s, X_te_s, y_tr_s, y_te_s = train_test_split(X_sds, y_sds, test_size=0.25, random_state=42, stratify=y_sds)

        lr_s = LogisticRegression(max_iter=1000).fit(X_tr_s, y_tr_s)
        rf_s = RandomForestClassifier(n_estimators=50, random_state=42).fit(X_tr_s, y_tr_s)

        y_p_lr_s = lr_s.predict(X_te_s)
        y_p_rf_s = rf_s.predict(X_te_s)

        self._sds_models = {
            "lr": lr_s,
            "rf": rf_s,
            "features": list(X_sds.columns),
            "sample_size": len(sds),
            "metrics": {
                "logistic_regression": {
                    "accuracy": round(accuracy_score(y_te_s, y_p_lr_s), 3),
                    "precision": round(precision_score(y_te_s, y_p_lr_s), 3),
                    "recall": round(recall_score(y_te_s, y_p_lr_s), 3),
                    "f1": round(f1_score(y_te_s, y_p_lr_s), 3),
                    "confusion_matrix": confusion_matrix(y_te_s, y_p_lr_s).tolist(),
                    "coefficients": dict(zip(X_sds.columns, lr_s.coef_[0].round(3)))
                },
                "random_forest": {
                    "accuracy": round(accuracy_score(y_te_s, y_p_rf_s), 3),
                    "precision": round(precision_score(y_te_s, y_p_rf_s), 3),
                    "recall": round(recall_score(y_te_s, y_p_rf_s), 3),
                    "f1": round(f1_score(y_te_s, y_p_rf_s), 3),
                    "confusion_matrix": confusion_matrix(y_te_s, y_p_rf_s).tolist(),
                    "importances": dict(zip(X_sds.columns, rf_s.feature_importances_.round(3)))
                }
            }
        }

    def predict_jds_salary_hike(
        self,
        big_data: float,
        maths_stats: float,
        coding: float,
        ai_ml: float,
        dashboard: float,
        model_type: str = "logistic_regression"
    ) -> Dict[str, Any]:
        """
        Calculates High Salary-Hike Probability (%) from candidate's technical skills profile.
        [MODEL OUTPUT on JDS Skill Traits]
        """
        model = self._jds_models["lr"] if model_type == "logistic_regression" else self._jds_models["rf"]
        input_data = pd.DataFrame([{
            "big_data_skills": big_data,
            "maths-stats_skills": maths_stats,
            "coding_skills": coding,
            "ai_and_ml_skills": ai_ml,
            "dashboard_and_storytelling_skills": dashboard
        }])

        proba = model.predict_proba(input_data)[0][1]
        hike_probability = round(float(proba) * 100, 1)

        # Ranked feature contributions
        if model_type == "logistic_regression":
            weights = self._jds_models["metrics"]["logistic_regression"]["coefficients"]
        else:
            weights = self._jds_models["metrics"]["random_forest"]["importances"]

        ranked_contributions = sorted(weights.items(), key=lambda x: abs(x[1]), reverse=True)
        factors = [
            {
                "feature": JDS_FEATURE_LABELS.get(k, k),
                "feature_code": k,
                "importance_weight": v,
                "user_score": input_data[k].iloc[0]
            }
            for k, v in ranked_contributions
        ]

        return {
            "high_hike_probability_pct": hike_probability,
            "model_prediction": "High Salary Hike" if hike_probability >= 50.0 else "Standard Salary Hike",
            "model_used": "Logistic Regression" if model_type == "logistic_regression" else "Random Forest",
            "top_contributing_factors": factors,
            "evaluation_metrics": self._jds_models["metrics"][model_type],
            "disclaimer": "Sample-level analytical model (N=139). Indicative of provided dataset; does not guarantee individual employer outcomes."
        }

    def predict_sds_success(
        self,
        neuroticism: float,
        extraversion: float,
        openness: float,
        agreeableness: float,
        conscientiousness: float,
        model_type: str = "logistic_regression"
    ) -> Dict[str, Any]:
        """
        Calculates Professional Success Profile Likelihood (%) from Big 5 personality traits.
        [MODEL OUTPUT on SDS Personality Traits]
        """
        model = self._sds_models["lr"] if model_type == "logistic_regression" else self._sds_models["rf"]
        input_data = pd.DataFrame([{
            "neuroticism": neuroticism,
            "extraversion": extraversion,
            "openness_to_experience": openness,
            "agreeableness": agreeableness,
            "conscientiousness": conscientiousness
        }])

        proba = model.predict_proba(input_data)[0][1]
        success_probability = round(float(proba) * 100, 1)

        if model_type == "logistic_regression":
            weights = self._sds_models["metrics"]["logistic_regression"]["coefficients"]
        else:
            weights = self._sds_models["metrics"]["random_forest"]["importances"]

        ranked_contributions = sorted(weights.items(), key=lambda x: abs(x[1]), reverse=True)
        factors = [
            {
                "feature": SDS_FEATURE_LABELS.get(k, k),
                "feature_code": k,
                "importance_weight": v,
                "user_score": input_data[k].iloc[0]
            }
            for k, v in ranked_contributions
        ]

        return {
            "success_probability_pct": success_probability,
            "model_prediction": "High Success Likelihood" if success_probability >= 50.0 else "Standard Trajectory",
            "model_used": "Logistic Regression" if model_type == "logistic_regression" else "Random Forest",
            "top_contributing_factors": factors,
            "evaluation_metrics": self._sds_models["metrics"][model_type],
            "disclaimer": "Observed association in supplied sample (N=161). This is NOT a psychological assessment and makes no causal claims."
        }

    def get_model_diagnostics(self) -> Dict[str, Any]:
        return {
            "jds": self._jds_models,
            "sds": self._sds_models
        }

# Global singleton
success_service = SuccessModelService()
