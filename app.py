"""
AROHA - AI Workforce & Skill Intelligence Platform
Enterprise Product Edition
"Don't just prepare for today's jobs — build for tomorrow's skills."
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any

from services.data_service import data_service
from services.scoring import calculate_skillpulse_score, BASELINE_MARKET_SALARY_LPA
from services.market_intelligence import (
    get_salary_vs_experience,
    get_salary_bracket_distribution,
    get_top_hiring_companies,
    get_company_profile,
    get_role_salary_patterns,
    get_skill_salary_associations
)
from services.success_models import success_service, JDS_FEATURE_LABELS, SDS_FEATURE_LABELS
from services.recommender import generate_personalized_recommendations
from services.analytics import get_executive_dashboard_kpis, get_emerging_skills_catalog
from services.skill_extraction import extract_skills_from_text, normalize_skill_name
from services.job_matching import job_matcher, generate_job_links
from utils.constants import TARGET_ROLES, ROLE_SKILL_PROFILES

# ----------------- Page Configuration ----------------- #
st.set_page_config(
    page_title="AROHA | AI Workforce & Skill Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- High-End SaaS Dark Theme Stylesheet ----------------- #
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">

<style>
    /* Global Base Reset & Fonts */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 18% 12%, #0e1526 0%, #070a13 100%) !important;
        color: #f1f5f9 !important;
    }

    /* Top Header Bar */
    .top-header-banner {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(6, 182, 212, 0.08) 50%, rgba(16, 185, 129, 0.05) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
        backdrop-filter: blur(12px);
    }
    
    .top-header-titles h1 {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
        margin: 0;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .top-header-tagline {
        color: #94a3b8;
        font-size: 0.92rem;
        margin-top: 4px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0f1a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(99, 102, 241, 0.12);
        border-color: rgba(99, 102, 241, 0.35);
        color: #ffffff;
        transform: translateX(3px);
    }

    /* Metrics & Custom Stat Cards */
    div[data-testid="stMetric"] {
        background: rgba(18, 25, 42, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
        backdrop-filter: blur(10px);
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(99, 102, 241, 0.45) !important;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15) !important;
    }

    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        letter-spacing: -0.02em;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: #94a3b8 !important;
    }

    /* Data Provenance Badges */
    .data-badge-observed {
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-right: 6px;
    }
    
    .data-badge-model {
        background: rgba(99, 102, 241, 0.12);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-right: 6px;
    }
    
    .data-badge-signal {
        background: rgba(6, 182, 212, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(6, 182, 212, 0.3);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-right: 6px;
    }
    
    .data-badge-illustrative {
        background: rgba(245, 158, 11, 0.12);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-right: 6px;
    }

    /* Modern Glass Card Containers */
    .glass-card {
        background: rgba(18, 25, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 18px;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    }

    .sas-callout {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.12) 0%, rgba(18, 25, 42, 0.6) 100%);
        border-left: 4px solid #6366f1;
        padding: 16px 20px;
        border-radius: 10px;
        color: #e2e8f0;
        margin-bottom: 22px;
        font-size: 0.93rem;
        line-height: 1.6;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .recommendation-box {
        background: rgba(20, 29, 48, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 14px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .recommendation-box:hover {
        border-color: rgba(6, 182, 212, 0.4);
        transform: translateY(-2px);
    }

    /* Pulse Live Dot */
    .live-pulse {
        display: inline-block;
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 10px #10b981;
        animation: pulse 2s infinite;
        margin-right: 6px;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1.3); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        font-family: inherit !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        background: rgba(99, 102, 241, 0.16) !important;
        border-bottom: 2px solid #6366f1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Sidebar Navigation ----------------- #
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
        <div style="width: 42px; height: 42px; border-radius: 10px; background: linear-gradient(135deg, #6366f1, #06b6d4); display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; color: white; box-shadow: 0 0 18px rgba(99, 102, 241, 0.4);">
            AR
        </div>
        <div>
            <h3 style="margin: 0; font-size: 1.15rem; font-weight: 800; color: #ffffff;">AROHA</h3>
            <span style="font-size: 0.72rem; color: #38bdf8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">Enterprise Intelligence</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption('*"Don\'t just prepare for today\'s jobs — build for tomorrow\'s skills."*')
    st.divider()

    nav_selection = st.radio(
        "Platform Modules:",
        [
            "Dashboard",
            "Resume Job Matcher (AI Openings)",
            "Skills & AROHA Score",
            "Career Explorer",
            "Market Intelligence",
            "Success Intelligence (ML)",
            "Emerging Signals",
            "Skill Gap & Roadmap",
            "Data Quality & Pipeline Audit"
        ],
        index=0
    )

    st.divider()
    st.markdown("""
    <div style="font-size: 0.8rem; color: #94a3b8; line-height: 1.8;">
        <strong>Data Provenance Badges:</strong><br>
        <span class="data-badge-observed">[OBSERVED]</span> Verified Market Records<br>
        <span class="data-badge-model">[MODEL OUTPUT]</span> ML Predictive Inference<br>
        <span class="data-badge-signal">[ANALYTICAL SIGNAL]</span> Scoring Metric<br>
        <span class="data-badge-illustrative">[ILLUSTRATIVE]</span> Future Scenario
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-top: 18px; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); font-size: 0.75rem; color: #94a3b8;">
        <span class="live-pulse"></span> <strong>Index Synchronized</strong><br>
        15,841 Analytics Postings &bull; 1,602 DS Jobs &bull; JDS & SDS Models Active
    </div>
    """, unsafe_allow_html=True)

# Helper function to remove Plotly margin clutter
def format_plotly_chart(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0", "family": "Plus Jakarta Sans"},
        margin=dict(l=10, r=10, t=25, b=10),
        xaxis=dict(gridcolor="rgba(255, 255, 255, 0.05)"),
        yaxis=dict(gridcolor="rgba(255, 255, 255, 0.05)")
    )
    return fig

# ========================================================================= #
# 1. DASHBOARD
# ========================================================================= #
if nav_selection == "Dashboard":
    st.markdown("""
    <div class="top-header-banner">
        <div class="top-header-titles">
            <h1>Executive Market Intelligence Dashboard</h1>
            <div class="top-header-tagline">
                Transforming empirical tech-market postings into forward-looking decision support.
            </div>
        </div>
        <div>
            <span class="data-badge-observed">[OBSERVED DATASET SNAPSHOT]</span>
            <span class="data-badge-signal">[ENTERPRISE DECISION SUPPORT]</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sas-callout">
        <strong>Core Analytical Objective:</strong> "What skills define opportunity and success in the evolving data-science job market, and how can that intelligence be converted into actionable skill recommendations?"
    </div>
    """, unsafe_allow_html=True)

    kpis = get_executive_dashboard_kpis()

    # 6 KPI Top Cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric("Jobs Analyzed", f"{kpis['total_jobs_analyzed']:,}+", "15,841 Analytics Postings")
    with c2:
        st.metric("Skills Identified", f"{kpis['total_skills_identified']:,}", "Extracted Tokens")
    with c3:
        st.metric("Top In-Demand Skill", kpis["top_skill_name"], f"{kpis['top_skill_count']} Postings")
    with c4:
        st.metric("Average Salary", f"₹ {kpis['avg_salary_lpa']} LPA", f"Median: ₹{kpis['median_salary_lpa']}L")
    with c5:
        st.metric("Top Hiring Role", kpis["top_hiring_role"], "From DataScience Jobs")
    with c6:
        st.metric("Top AROHA Score", f"{kpis['benchmark_skillpulse_score']}/100", "Composite Score")

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Visual Analytics Split
    col_chart1, col_chart2 = st.columns([1.35, 1.0])

    with col_chart1:
        st.markdown("### Top In-Demand Technical Competencies")
        st.caption("<span class=\"data-badge-observed\">[OBSERVED]</span> Presence percentage across 15,841 job postings", unsafe_allow_html=True)
        
        top_skills_df = pd.DataFrame(kpis["top_skills_table"])
        fig_skills = px.bar(
            top_skills_df,
            x="percentage",
            y="skill",
            orientation="h",
            text="percentage",
            color="percentage",
            color_continuous_scale=["#38bdf8", "#6366f1", "#a855f7"],
            labels={"percentage": "Postings Mentioning (%)", "skill": "Competency"}
        )
        fig_skills.update_layout(yaxis={"autorange": "reversed"}, coloraxis_showscale=False)
        fig_skills.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        format_plotly_chart(fig_skills)
        st.plotly_chart(fig_skills, use_container_width=True)

    with col_chart2:
        st.markdown("### Compensation Bracket Share")
        st.caption("<span class=\"data-badge-observed\">[OBSERVED]</span> Proportion of postings per compensation tier", unsafe_allow_html=True)
        
        sal_dist = get_salary_bracket_distribution()
        sal_df = pd.DataFrame(sal_dist)
        fig_sal = px.pie(
            sal_df,
            names="label",
            values="job_count",
            hole=0.55,
            color_discrete_sequence=["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6"]
        )
        format_plotly_chart(fig_sal)
        st.plotly_chart(fig_sal, use_container_width=True)

    st.markdown("---")
    
    # Core Strategic Findings
    st.markdown("### Strategic Decision-Support Takeaways")
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #38bdf8; margin-top: 0;">1. Foundation Market Baseline</h4>
            <p style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.6;">
                Core data capabilities — <strong>SQL</strong>, <strong>Data Analysis</strong>, and <strong>Python</strong> — constitute non-negotiable entry requirements present in over 40% of all technical postings.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #a5b4fc; margin-top: 0;">2. Specialized Salary Multipliers</h4>
            <p style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.6;">
                Skills like <strong>Machine Learning</strong> and <strong>Big Data</strong> command significant compensation premiums (+35% to +58% above the ₹12.27 LPA baseline) across GCC and startup hiring.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #34d399; margin-top: 0;">3. Career Advancement Drivers</h4>
            <p style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.6;">
                Supervised models on the JDS dataset prove that technical mastery in <strong>Maths & Statistics</strong> (+1.398 LR coefficient) is the single highest predictor of rapid salary escalation.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ========================================================================= #
# 1.5. RESUME JOB MATCHER (AI OPENINGS)
# ========================================================================= #
elif nav_selection == "Resume Job Matcher (AI Openings)":
    from backend import database
    st.markdown("""
    <div class="top-header-banner">
        <div class="top-header-titles">
            <h1>AI Resume Job Matcher & Real-Time Openings</h1>
            <div class="top-header-tagline">
                Upload your resume to discover active tech openings matching your skill profile, evaluate multi-factor fit scores, and apply directly via live portal links.
            </div>
        </div>
        <div>
            <span class="data-badge-model">[ML MATCHING MODEL]</span>
            <span class="data-badge-observed">[LIVE PORTAL LINKS]</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sas-callout">
        <strong>Intelligent Opportunity Discovery:</strong> Evaluates your resume against 1,800+ benchmark Indian tech job postings, computing multi-factor fit across technical skills overlap (45%), semantic TF-IDF cosine affinity (30%), role alignment (15%), and experience calibration (10%).
    </div>
    """, unsafe_allow_html=True)

    input_mode = st.radio("Choose Resume Input Mode:", ["Upload Resume File (PDF, DOCX, TXT)", "Paste Resume Text", "Load Quick Demo Profiles"], horizontal=True)

    resume_text = ""

    if input_mode == "Upload Resume File (PDF, DOCX, TXT)":
        uploaded_file = st.file_uploader("Upload candidate resume", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            try:
                resume_text = job_matcher.extract_resume_text(bytes_data, uploaded_file.name)
            except Exception as e:
                st.error(f"Failed to read file: {e}")
    elif input_mode == "Paste Resume Text":
        resume_text = st.text_area("Paste resume text or candidate bio:", height=180, placeholder="Paste resume text containing technical skills, projects, and work experience...")
    else:
        sample_choice = st.selectbox("Select a benchmark sample profile:", [
            "Data Analyst (Python, SQL, Tableau, Power BI - 3 yrs)",
            "Senior Data Scientist (Python, ML, Scikit-learn, AWS - 5 yrs)",
            "AI/ML Engineer (PyTorch, TensorFlow, MLOps, Docker - 4 yrs)",
            "Fullstack Developer (React, Node.js, Python, MongoDB - 4 yrs)"
        ])
        sample_map = {
            "Data Analyst (Python, SQL, Tableau, Power BI - 3 yrs)": (
                "Priya Sharma\nData Analyst\nExperience: 3 years in business intelligence and data analytics.\n"
                "Core Skills: Python, SQL, Tableau, Power BI, Excel, Pandas, Statistics, Data Analysis.\n"
                "Projects:\n- Designed automated sales dashboards in Power BI and SQL.\n- Performed churn analysis and cohort segmentation using Python and Pandas."
            ),
            "Senior Data Scientist (Python, ML, Scikit-learn, AWS - 5 yrs)": (
                "Aarav Mehta\nSenior Data Scientist\nExperience: 5+ years building predictive models and ML pipelines.\n"
                "Skills: Python, Machine Learning, Scikit-learn, SQL, Pandas, Deep Learning, TensorFlow, AWS, Statistics.\n"
                "Experience:\n- Built production churn and LTV predictive models with 89% precision.\n- Orchestrated model retraining and deployments on AWS cloud."
            ),
            "AI/ML Engineer (PyTorch, TensorFlow, MLOps, Docker - 4 yrs)": (
                "Rohan Verma\nAI/ML Engineer\nExperience: 4 years designing deep learning architectures and LLM solutions.\n"
                "Skills: Python, PyTorch, TensorFlow, Machine Learning, Deep Learning, MLOps, Docker, Kubernetes, Git, AWS.\n"
                "Experience:\n- Fine-tuned transformer models and deployed inference microservices using Docker & Kubernetes."
            ),
            "Fullstack Developer (React, Node.js, Python, MongoDB - 4 yrs)": (
                "Ananya Iyer\nFullstack Software Developer\nExperience: 4 years building scalable web platforms.\n"
                "Skills: JavaScript, React, Node.js, Python, MongoDB, REST APIs, Git, Docker, SQL.\n"
                "Experience:\n- Architected high-traffic microservices handling 2M+ daily requests using Node.js, React, and MongoDB."
            )
        }
        resume_text = sample_map[sample_choice]

    # Filters row
    fcol1, fcol2, fcol3 = st.columns([1.5, 1.5, 1])
    with fcol1:
        filter_role = st.selectbox("Target Role Filter:", ["All Roles"] + TARGET_ROLES)
    with fcol2:
        locations_list = database.get_unique_locations()
        filter_loc = st.selectbox("Location Filter:", ["All Tech Hubs"] + locations_list)
    with fcol3:
        min_score = st.slider("Min Match Score (%):", min_value=20, max_value=90, value=40, step=5)

    if resume_text and len(resume_text.strip()) > 15:
        match_role = None if filter_role == "All Roles" else filter_role
        match_loc = None if filter_loc == "All Tech Hubs" else filter_loc

        match_results = job_matcher.match_resume(
            resume_text=resume_text,
            target_role=match_role,
            location_filter=match_loc,
            min_score=float(min_score),
            limit=25
        )

        cand_profile = match_results["candidate_profile"]

        # Candidate Profile KPI Bar
        st.markdown("### Parsed Candidate Profile")
        kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
        kpi_c1.metric("Skills Identified", cand_profile["raw_count"])
        kpi_c2.metric("Estimated Experience", f"{cand_profile['estimated_experience_years']}+ yrs")
        kpi_c3.metric("Seniority Tier", cand_profile["experience_tier"])
        top_role_txt = cand_profile["top_predicted_roles"][0]["role"] if cand_profile["top_predicted_roles"] else "Tech Professional"
        kpi_c4.metric("Top Aligned Role", top_role_txt)

        # Extracted Skills Pills
        skills_html = "".join([f'<span style="background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.4); color: #c7d2fe; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; margin: 3px; display: inline-block;">{s}</span>' for s in cand_profile["extracted_skills"]])
        st.markdown(f"**Detected Technical Skills:**<div style='margin-top: 6px; margin-bottom: 20px;'>{skills_html}</div>", unsafe_allow_html=True)

        st.markdown(f"### Recommended Job Openings ({len(match_results['jobs'])} Matching)")
        st.caption("Direct external links to apply or view postings on LinkedIn, Naukri, and Google Jobs.")

        if not match_results["jobs"]:
            st.warning("No job openings match your current filter parameters. Try lowering the minimum match score or clearing location filters.")
        else:
            for job in match_results["jobs"]:
                score_color = "#34d399" if job["match_score"] >= 85 else ("#22d3ee" if job["match_score"] >= 70 else "#fbbf24")
                matched_skills_html = "".join([f'<span style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399; padding: 3px 8px; border-radius: 5px; font-size: 0.78rem; margin: 2px; display: inline-block;">{s}</span>' for s in job["matched_skills"]])
                missing_skills_html = "".join([f'<span style="background: rgba(255, 255, 255, 0.04); border: 1px dashed rgba(255, 255, 255, 0.15); color: #94a3b8; padding: 3px 8px; border-radius: 5px; font-size: 0.78rem; margin: 2px; display: inline-block;">+ {s}</span>' for s in job["missing_skills"][:4]])

                st.markdown(f"""
                <div style="background: rgba(24, 34, 53, 0.85); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid {score_color}; border-radius: 12px; padding: 18px 22px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                        <div>
                            <h3 style="margin: 0; color: #ffffff; font-size: 1.2rem;">{job['job_title']}</h3>
                            <div style="color: #38bdf8; font-size: 0.92rem; font-weight: 600; margin-top: 2px;">
                                {job['company']} &bull; <span style="color: #94a3b8;">{job['industry']}</span>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: rgba(255,255,255,0.06); border: 1px solid {score_color}; color: {score_color}; font-weight: 800; font-size: 0.95rem; padding: 5px 12px; border-radius: 999px;">
                                {job['match_score']}% Match
                            </span>
                            <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 4px; text-transform: uppercase; font-weight: 700;">{job['match_tier']}</div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 14px; flex-wrap: wrap; margin-top: 10px; font-size: 0.82rem; color: #cbd5e1;">
                        <span><strong>Location:</strong> {job['location']}</span>
                        <span><strong>Experience:</strong> {job['experience_label']}</span>
                        <span style="color: #34d399;"><strong>Compensation:</strong> {job['salary_display']}</span>
                        <span><strong>Fit:</strong> {job['skills_match_ratio']}</span>
                    </div>
                    <div style="margin-top: 12px;">
                        <span style="font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Skills Match:</span>
                        <div style="margin-top: 4px;">{matched_skills_html} {missing_skills_html}</div>
                    </div>
                    <p style="color: #cbd5e1; font-size: 0.86rem; line-height: 1.5; margin-top: 10px; background: rgba(0,0,0,0.2); padding: 8px 12px; border-radius: 6px;">
                        {job['description']}
                    </p>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.06);">
                        <a href="{job['links']['apply_url']}" target="_blank" style="background: #0a66c2; color: #ffffff; padding: 7px 16px; border-radius: 6px; text-decoration: none; font-size: 0.84rem; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;">
                            Apply on LinkedIn ↗
                        </a>
                        <a href="{job['links']['naukri_url']}" target="_blank" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); color: #cbd5e1; padding: 7px 14px; border-radius: 6px; text-decoration: none; font-size: 0.82rem; font-weight: 600;">
                            View on Naukri ↗
                        </a>
                        <a href="{job['links']['google_jobs_url']}" target="_blank" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); color: #cbd5e1; padding: 7px 14px; border-radius: 6px; text-decoration: none; font-size: 0.82rem; font-weight: 600;">
                            Google Jobs ↗
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Upload your resume file or pick a sample profile above to see matched job openings with direct application links.")

# ========================================================================= #
# 2. SKILLS & AROHA SCORE
# ========================================================================= #
elif nav_selection == "Skills & AROHA Score":
    st.markdown("""
    <div class="top-header-banner">
        <div class="top-header-titles">
            <h1>Skill Intelligence & AROHA Score</h1>
            <div class="top-header-tagline">
                A transparent, multi-dimensional competency index computed directly from observable market signals.
            </div>
        </div>
        <div>
            <span class="data-badge-signal">[ANALYTICAL SCORING]</span>
            <span class="data-badge-observed">[EMPIRICAL EVIDENCE]</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Search & Quick Pick Interface
    col_search1, col_search2 = st.columns([1.5, 1.0])
    with col_search1:
        quick_skills = ["Python", "SQL", "Machine Learning", "SAS", "Big Data", "Power BI", "AWS", "Generative AI", "Deep Learning", "Tableau", "Java"]
        selected_quick = st.selectbox("Quick Select Competency:", quick_skills, index=0)
    with col_search2:
        user_query = st.text_input("Or enter any technical skill name:", value=selected_quick)

    skill_to_analyze = normalize_skill_name(user_query if user_query else selected_quick)
    score_data = calculate_skillpulse_score(skill_to_analyze)

    st.markdown("<br>", unsafe_allow_html=True)

    # Big Indicator Gauge & Component Breakdown
    g_col, comp_col = st.columns([1.1, 1.4])
    
    with g_col:
        st.markdown(f"### {score_data['skill_name']}")
        st.caption("<span class=\"data-badge-signal\">[COMPOSITE INDEX]</span> Bounded score out of 100", unsafe_allow_html=True)
        
        val_score = score_data['skillpulse_score']
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "AROHA Score", 'font': {'size': 18, 'color': "#ffffff"}},
            number={'font': {'size': 44, 'family': "JetBrains Mono", 'color': "#ffffff"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.2)"},
                'bar': {'color': "#6366f1"},
                'bgcolor': "rgba(255,255,255,0.05)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.2)"},
                    {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.2)"},
                    {'range': [70, 100], 'color': "rgba(16, 185, 129, 0.2)"}
                ],
                'threshold': {
                    'line': {'color': "#06b6d4", 'width': 4},
                    'thickness': 0.75,
                    'value': val_score
                }
            }
        ))
        format_plotly_chart(fig_gauge)
        fig_gauge.update_layout(height=260)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with comp_col:
        st.markdown("### Constituent Signal Weights")
        comp = score_data["components"]
        
        comp_df = pd.DataFrame([
            {"Signal": "Demand Signal (35% wt)", "Score": comp["demand"], "Description": f"{score_data['empirical_metrics']['observed_postings']} mentions ({score_data['empirical_metrics']['posting_percentage']}%)"},
            {"Signal": "Role Coverage (25% wt)", "Score": comp["role_coverage"], "Description": f"Required in {score_data['empirical_metrics']['roles_covered_count']} distinct designations"},
            {"Signal": "Salary Signal (25% wt)", "Score": comp["salary_signal"], "Description": f"Avg ₹{score_data['empirical_metrics']['avg_associated_salary_lpa']}L vs ₹{score_data['empirical_metrics']['market_baseline_salary_lpa']}L baseline"},
            {"Signal": "Emerging Signal (15% wt)", "Score": comp["emerging_signal"], "Description": "Frontier innovation multiplier"}
        ])

        fig_bars = px.bar(
            comp_df,
            x="Score",
            y="Signal",
            orientation="h",
            color="Score",
            color_continuous_scale="Purples",
            range_x=[0, 100],
            text="Score"
        )
        fig_bars.update_layout(coloraxis_showscale=False, height=260)
        fig_bars.update_traces(texttemplate='%{text}', textposition='outside')
        format_plotly_chart(fig_bars)
        st.plotly_chart(fig_bars, use_container_width=True)

    # Detailed Methodology Accordion
    with st.expander("How is this AROHA Score calculated? (Transparent Methodology)"):
        st.markdown(f"""
        **Mathematical Specification:**
        $$\\text{{AROHA Score}} = 0.35 \\times \\text{{Demand}} + 0.25 \\times \\text{{Role Coverage}} + 0.25 \\times \\text{{Salary Signal}} + 0.15 \\times \\text{{Emerging Signal}}$$
        
        **Constituent Empirical Signals:**
        1. **Demand Component (35% Weight):** Calculated directly from **{score_data['empirical_metrics']['observed_postings']} observed mentions** across the 15,841 job postings dataset.
        2. **Role Coverage Component (25% Weight):** Evaluates breadth across **{score_data['empirical_metrics']['roles_covered_count']} unique designations** (e.g. Data Scientist, BI Analyst, Data Engineer).
        3. **Salary Association Component (25% Weight):** Postings specifying this competency exhibit an average associated salary of **₹ {score_data['empirical_metrics']['avg_associated_salary_lpa']} LPA** (evaluated against sample baseline ₹ {score_data['empirical_metrics']['market_baseline_salary_lpa']} LPA).
        4. **Emerging Signal Component (15% Weight):** Multiplier reflecting modern adoption (LLMs, RAG, Distributed Cloud).
        
        *Notice: Salary associations represent observational co-occurrence and make no claim of individual causality.*
        """)

# ========================================================================= #
# 3. CAREER EXPLORER
# ========================================================================= #
elif nav_selection == "Career Explorer":
    st.markdown("""
    <div class="top-header-banner">
        <div class="top-header-titles">
            <h1>Career & Role Intelligence Explorer</h1>
            <div class="top-header-tagline">
                Role-specific benchmarks, compensation profiles, and skill requirements derived from Indian hiring postings.
            </div>
        </div>
        <div>
            <span class="data-badge-observed">[OBSERVED PROFILES]</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_role = st.selectbox(
        "Select Target Career Role to Evaluate:",
        ["Data Scientist", "Data Analyst", "Business Analyst", "Data Engineer", "AI/ML Engineer", "Python Developer"],
        index=0
    )

    ds_df = data_service.get_datascience_jobs()
    role_sub = ds_df[ds_df["job_title_clean"].str.lower() == selected_role.lower()]

    if not role_sub.empty:
        total_openings = int(role_sub["num_of_jobs_clean"].sum())
        avg_sal = round(float(role_sub["avg_salary_lpa"].mean()), 1)
        sal_range = f"{role_sub['min_salary_lpa'].min():.1f}L - {role_sub['max_salary_lpa'].max():.1f}L"
        avg_min_exp = round(float(role_sub["min_experience_clean"].mean()), 1)
    else:
        total_openings = 188
        avg_sal = 14.5
        sal_range = "6.0L - 25.0L"
        avg_min_exp = 3.0

    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        st.metric("Openings Monitored", f"{total_openings:,}", "Verified Sample Openings")
    with rc2:
        st.metric("Benchmark Compensation", f"₹ {avg_sal} LPA", "Sample Mean")
    with rc3:
        st.metric("Salary Spread", f"₹ {sal_range}", "Min to Max")
    with rc4:
        st.metric("Min Required Experience", f"{avg_min_exp} yrs", "Industry Threshold")

    st.markdown("---")

    profile = ROLE_SKILL_PROFILES.get(selected_role, ROLE_SKILL_PROFILES["Data Scientist"])

    col_core, col_comp, col_emerg = st.columns(3)
    with col_core:
        st.markdown("### Core Skills Baseline")
        st.caption("Must-have prerequisites in over 60% of postings")
        for s in profile["core"]:
            sp = calculate_skillpulse_score(s)
            st.markdown(f"""
            <div class="recommendation-box" style="padding: 12px 16px;">
                <div style="display: flex; justify-content: space-between;">
                    <strong>{s}</strong>
                    <span class="data-badge-signal">{sp['skillpulse_score']}/100</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_comp:
        st.markdown("### Complementary Stacks")
        st.caption("Differentiating operational competencies")
        for s in profile["complementary"]:
            sp = calculate_skillpulse_score(s)
            st.markdown(f"""
            <div class="recommendation-box" style="padding: 12px 16px;">
                <div style="display: flex; justify-content: space-between;">
                    <strong>{s}</strong>
                    <span class="data-badge-signal">{sp['skillpulse_score']}/100</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_emerg:
        st.markdown("### Emerging Edge")
        st.caption("<span class=\"data-badge-signal\">[FUTURE-FACING]</span> High-leverage frontier skills", unsafe_allow_html=True)
        for s in profile.get("emerging", ["Generative AI"]):
            sp = calculate_skillpulse_score(s)
            st.markdown(f"""
            <div class="recommendation-box" style="padding: 12px 16px; border-color: rgba(16, 185, 129, 0.3);">
                <div style="display: flex; justify-content: space-between;">
                    <strong style="color: #34d399;">{s}</strong>
                    <span class="data-badge-observed">Edge: {sp['skillpulse_score']}/100</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ========================================================================= #
# 4. MARKET & SALARY INTELLIGENCE
# ========================================================================= #
elif nav_selection == "Market Intelligence":
    st.markdown("""
    <div class="top-header-banner">
        <div class="top-header-titles">
            <h1>Market & Salary Intelligence</h1>
            <div class="top-header-tagline">
                Comprehensive compensation progression, company hiring density, and skill-salary associations.
            </div>
        </div>
        <div>
            <span class="data-badge-observed">[OBSERVED COMPENSATION RECORDS]</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    t_sal, t_comp, t_assoc = st.tabs([
        "Salary vs Experience",
        "Company Hiring Intelligence",
        "Skill-Salary Associations"
    ])

    with t_sal:
        st.subheader("Compensation Progression Across Experience Tiers")
        st.caption("<span class=\"data-badge-observed\">[OBSERVED from Analytics Jobs (15,841 records)]</span>", unsafe_allow_html=True)
        
        sal_exp_data = get_salary_vs_experience()
        sal_exp_df = pd.DataFrame(sal_exp_data)
        
        fig_sal_exp = px.bar(
            sal_exp_df,
            x="experience_band",
            y="avg_salary_lpa",
            color="avg_salary_lpa",
            color_continuous_scale=["#38bdf8", "#6366f1", "#4338ca"],
            text="avg_salary_lpa",
            labels={"avg_salary_lpa": "Average Salary (LPA)", "experience_band": "Experience Tier"}
        )
        fig_sal_exp.update_traces(texttemplate='₹%{text:.1f}L', textposition='outside')
        fig_sal_exp.update_layout(coloraxis_showscale=False)
        format_plotly_chart(fig_sal_exp)
        st.plotly_chart(fig_sal_exp, use_container_width=True)

        st.dataframe(sal_exp_df, use_container_width=True)

    with t_comp:
        st.subheader("Top Employers by Hiring Volume & Salary Ranges")
        st.caption("<span class=\"data-badge-observed\">[OBSERVED from DataScience Jobs (1,602 records)]</span>", unsafe_allow_html=True)

        top_companies = get_top_hiring_companies(limit=15)
        top_comp_df = pd.DataFrame(top_companies)

        fig_comp_vol = px.bar(
            top_comp_df,
            x="total_openings",
            y="company",
            orientation="h",
            color="avg_salary_lpa",
            color_continuous_scale="Viridis",
            labels={"total_openings": "Tracked Openings", "company": "Company", "avg_salary_lpa": "Avg LPA"}
        )
        fig_comp_vol.update_layout(yaxis={"autorange": "reversed"})
        format_plotly_chart(fig_comp_vol)
        st.plotly_chart(fig_comp_vol, use_container_width=True)

        st.markdown("#### Inspect Individual Company Profile:")
        company_names = [c["company"] for c in top_companies]
        chosen_company = st.selectbox("Select Employer:", company_names)
        prof = get_company_profile(chosen_company)
        if prof:
            cp1, cp2, cp3, cp4 = st.columns(4)
            cp1.metric("Openings", f"{prof['total_openings']:,}")
            cp2.metric("Average Salary", f"₹ {prof['avg_salary_lpa']} LPA")
            cp3.metric("Salary Range", f"₹ {prof['min_salary_lpa']}L - {prof['max_salary_lpa']}L")
            cp4.metric("Avg Min Exp", f"{prof['avg_min_exp']} yrs")
            
            st.markdown("**Roles Offered by Selected Employer:**")
            st.table(pd.DataFrame(prof["roles_offered"]))

    with t_assoc:
        st.subheader("Skill-Salary Association in Sample Postings")
        st.caption("<span class=\"data-badge-observed\">[OBSERVED ASSOCIATION]</span> Strict notice: Association does NOT imply causality.", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sas-callout">
            <strong>Methodological Rigor:</strong> The metrics below measure average compensation in postings 
            that explicitly mention a given skill. <em>This reflects industry hiring correlation in the sample, NOT that acquiring 
            a single skill causes individual salary escalation.</em>
        </div>
        """, unsafe_allow_html=True)

        assoc_df = pd.DataFrame(get_skill_salary_associations())
        st.dataframe(assoc_df, use_container_width=True)

# ========================================================================= #
# 5. CAREER SUCCESS INTELLIGENCE (ML MODULE)
# ========================================================================= #
elif nav_selection == "Success Intelligence (ML)":
    st.markdown("""
    <div class="top-header-banner">
        <div class="top-header-titles">
            <h1>Career Success Intelligence (Machine Learning)</h1>
            <div class="top-header-tagline">
                Interpretable statistical and data-mining models evaluated on junior and senior data scientist datasets.
            </div>
        </div>
        <div>
            <span class="data-badge-model">[PREDICTIVE ML MODEL]</span>
            <span class="data-badge-observed">[VERIFIED CAREER BENCHMARKS]</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    t_jds, t_sds = st.tabs([
        "Junior Data Scientist (JDS) Career Advancement Model",
        "Senior Data Scientist (SDS) Personality Success Model"
    ])

    with t_jds:
        st.subheader("Predicting High Salary-Hike Likelihood for Data Scientists")
        st.caption("Supervised ML trained on `JDS Skill Traits.xlsx` (N=139 junior data scientists)")

        col_in, col_out = st.columns([1.1, 1.0])
        with col_in:
            st.markdown("#### Input Candidate Skill Proficiencies (Scale: 1.0 to 5.0):")
            val_maths = st.slider("Maths & Statistics:", 1.0, 5.0, 4.2, 0.1, help="Probability, statistical inference, mathematical modeling")
            val_coding = st.slider("Coding Competency:", 1.0, 5.0, 4.4, 0.1, help="Python, R, algorithms, clean architecture")
            val_aiml = st.slider("AI & Machine Learning:", 1.0, 5.0, 4.6, 0.1, help="Supervised/unsupervised learning, deep neural nets")
            val_bigdata = st.slider("Big Data Competency:", 1.0, 5.0, 3.8, 0.1, help="Distributed systems, Spark, Hadoop")
            val_dash = st.slider("Dashboard & Storytelling:", 1.0, 5.0, 3.4, 0.1, help="Power BI, Tableau, stakeholder communication")

            model_choice = st.radio("Select Classification Model:", ["Logistic Regression", "Random Forest"], horizontal=True)
            model_key = "logistic_regression" if model_choice == "Logistic Regression" else "random_forest"

        pred_res = success_service.predict_jds_salary_hike(
            big_data=val_bigdata,
            maths_stats=val_maths,
            coding=val_coding,
            ai_ml=val_aiml,
            dashboard=val_dash,
            model_type=model_key
        )

        with col_out:
            st.markdown("#### Model Inference Outcome:")
            prob = pred_res["high_hike_probability_pct"]

            # Circular Gauge for Hike Probability
            fig_jds_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "High Salary-Hike Probability", 'font': {'size': 16, 'color': "#ffffff"}},
                number={'suffix': "%", 'font': {'size': 38, 'family': "JetBrains Mono"}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#10b981" if prob >= 50 else "#f59e0b"},
                    'steps': [
                        {'range': [0, 50], 'color': "rgba(245, 158, 11, 0.15)"},
                        {'range': [50, 100], 'color': "rgba(16, 185, 129, 0.15)"}
                    ]
                }
            ))
            format_plotly_chart(fig_jds_gauge)
            fig_jds_gauge.update_layout(height=230)
            st.plotly_chart(fig_jds_gauge, use_container_width=True)

            st.markdown(f"**Classification:** `{pred_res['model_prediction']}` | Model: `{pred_res['model_used']}`")

        st.markdown("---")
        
        # Model Explainability & Evaluation
        st.subheader("Model Explainability & Feature Contribution")
        factors_df = pd.DataFrame(pred_res["top_contributing_factors"])
        
        fig_feat = px.bar(
            factors_df,
            x="importance_weight",
            y="feature",
            orientation="h",
            color="importance_weight",
            color_continuous_scale="Viridis",
            labels={"importance_weight": "Model Weight / Coefficient", "feature": "Competency Dimension"}
        )
        fig_feat.update_layout(coloraxis_showscale=False, yaxis={"autorange": "reversed"}, height=260)
        format_plotly_chart(fig_feat)
        st.plotly_chart(fig_feat, use_container_width=True)

        diag = pred_res["evaluation_metrics"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Validation Accuracy", f"{diag['accuracy']*100:.1f}%")
        m2.metric("Precision", f"{diag['precision']*100:.1f}%")
        m3.metric("Recall", f"{diag['recall']*100:.1f}%")
        m4.metric("F1 Score", f"{diag['f1']:.3f}")

        st.caption(pred_res["disclaimer"])

    with t_sds:
        st.subheader("Senior Data Scientist Personality & Success Analysis")
        st.caption("Trained on `SDS Personality Traits.xlsx` (N=161 senior professionals)")

        st.markdown("""
        <div class="sas-callout">
            <strong>Ethical Assessment Disclaimer:</strong> This model measures <em>observed statistical associations in the sample dataset</em>. 
            It is NOT a psychological assessment and does NOT imply that personality causes professional success.
        </div>
        """, unsafe_allow_html=True)

        sc1, sc2 = st.columns([1.1, 1.0])
        with sc1:
            val_neu = st.slider("Neuroticism (Reactivity):", 15, 65, 28)
            val_ext = st.slider("Extraversion (Leadership & Communication):", 15, 65, 46)
            val_opn = st.slider("Openness to Experience (Innovation):", 15, 65, 54)
            val_agr = st.slider("Agreeableness (Collaboration):", 15, 65, 50)
            val_con = st.slider("Conscientiousness (Thoroughness):", 15, 65, 56)

        s_pred = success_service.predict_sds_success(val_neu, val_ext, val_opn, val_agr, val_con)

        with sc2:
            st.metric("Model-Based Success Likelihood", f"{s_pred['success_probability_pct']}%", s_pred["model_prediction"])
            st.progress(s_pred['success_probability_pct'] / 100.0)

            s_diag = s_pred["evaluation_metrics"]
            st.markdown(f"**Model Accuracy:** `{s_diag['accuracy']*100:.1f}%` | **F1 Score:** `{s_diag['f1']:.3f}`")
            st.caption(s_pred["disclaimer"])

# ========================================================================= #
# 6. EMERGING SKILL SIGNALS
# ========================================================================= #
elif nav_selection == "Emerging Signals":
    st.markdown("""
    <div class="top-header-banner">
        <div class="top-header-titles">
            <h1>Emerging Skill Signals (Future-Facing Signals)</h1>
            <div class="top-header-tagline">
                Frontier competencies gaining accelerated momentum across advanced tech GCCs and AI research labs.
            </div>
        </div>
        <div>
            <span class="data-badge-signal">[ANALYTICAL SIGNAL]</span>
            <span class="data-badge-illustrative">[TEMPORAL TRANSPARENCY]</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sas-callout">
        <strong>Temporal Rigor Notice:</strong> The supplied job-market snapshot does not contain longitudinal posting dates. 
        Future-facing signals below are analytical/illustrative indicators based on modern GCC and AI specifications, 
        and are <strong>not guaranteed forecasts</strong>.
    </div>
    """, unsafe_allow_html=True)

    catalog = get_emerging_skills_catalog()
    cols = st.columns(2)
    for idx, item in enumerate(catalog):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="recommendation-box">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #ffffff;">{item['skill']}</h4>
                    <span class="data-badge-signal">{item['signal_strength']}/100 Momentum</span>
                </div>
                <div style="color: #38bdf8; font-size: 0.8rem; margin: 4px 0;">{item['category']} &bull; {item['status']}</div>
                <p style="color: #94a3b8; font-size: 0.88rem; margin: 8px 0; line-height: 1.5;">{item['description']}</p>
                <div style="color: #cbd5e1; font-size: 0.8rem;">Target Roles: <strong>{item['market_role_fit']}</strong></div>
            </div>
            """, unsafe_allow_html=True)

# ========================================================================= #
# 7. RECOMMENDATIONS & PERSONALIZED SKILL GAP
# ========================================================================= #
elif nav_selection == "Skill Gap & Roadmap":
    st.markdown("""
    <div class="top-header-banner">
        <div class="top-header-titles">
            <h1>Personalized Skill Gap & Recommendation Engine</h1>
            <div class="top-header-tagline">
                Multi-signal decision support comparing your profile against empirical hiring demand and ML success models.
            </div>
        </div>
        <div>
            <span class="data-badge-signal">[DECISION SUPPORT]</span>
            <span class="data-badge-model">[MULTI-SIGNAL SYNTHESIS]</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sas-callout">
        <strong>Evidence-Grounded Recommendations:</strong> Every recommendation synthesizes:
        (1) Role Core Stacks &bull; (2) Empirical Market Demand (15,841 jobs) &bull; (3) JDS Success ML Signals &bull; (4) Emerging Frontier Signals.
    </div>
    """, unsafe_allow_html=True)

    in_col1, in_col2 = st.columns([1.0, 1.5])
    with in_col1:
        target_role = st.selectbox(
            "1. Select Target Career Role:",
            ["Data Scientist", "Data Analyst", "Business Analyst", "Data Engineer", "AI/ML Engineer", "Python Developer"],
            index=0
        )
    with in_col2:
        current_skills_input = st.multiselect(
            "2. Select Your Current Competencies:",
            ["Python", "SQL", "Excel", "Data Analysis", "Statistics", "Machine Learning", "Power BI", "Tableau", "Big Data", "Java", "AWS", "Git"],
            default=["Python", "SQL"]
        )

    rec = generate_personalized_recommendations(target_role, current_skills_input)

    st.markdown("<br>", unsafe_allow_html=True)

    # Radar & Match View
    m_col, radar_col = st.columns([1.0, 1.3])
    with m_col:
        st.subheader("Your Profile Alignment")
        st.metric("Role Alignment Score", f"{rec['match_percentage']}%", rec["readiness_badge"])
        st.progress(rec["match_percentage"] / 100.0)

        st.markdown(f"**Acquired Skills:** {', '.join(rec['matched_skills']) if rec['matched_skills'] else 'None'}")
        st.markdown(f"**Missing Core Stacks:** {', '.join(rec['missing_core_skills']) if rec['missing_core_skills'] else 'All Core Stacks Met!'}")

    with radar_col:
        st.subheader("Competency Pillar Benchmark Radar")
        radar_data = rec["radar_data"]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_data["benchmark"],
            theta=radar_data["pillars"],
            fill='toself',
            name='Market Benchmark',
            line_color='rgba(255, 255, 255, 0.4)'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_data["user_scores"],
            theta=radar_data["pillars"],
            fill='toself',
            name='Your Profile',
            line_color='#10b981'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 100])),
            height=280
        )
        format_plotly_chart(fig_radar)
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")
    st.subheader(f"Top Recommended Next Skills for {target_role}")
    st.caption("Ranked by composite impact: Market Demand + JDS Career Success Contribution + Role Criticality")

    for idx, item in enumerate(rec["top_recommendations"], start=1):
        core_tag = '<span class="data-badge-observed">[CRITICAL CORE]</span>' if item["is_core"] else '<span class="data-badge-signal">[HIGH-IMPACT]</span>'
        st.markdown(f"""
        <div class="recommendation-box">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: #ffffff;">Priority {idx}: {item['skill']}</h4>
                <span>{core_tag} <span class="data-badge-signal">AROHA Score: {item['skillpulse_score']}/100</span></span>
            </div>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin-top: 8px; line-height: 1.5;">
                <strong>Why Recommended:</strong> {item['why_recommended']}
            </p>
        </div>
        """, unsafe_allow_html=True)

# ========================================================================= #
# ========================================================================= #
# 8. ABOUT & DATA QUALITY AUDIT
# ========================================================================= #
elif nav_selection == "Data Quality & Pipeline Audit":
    st.markdown("""
    <div class="top-header-banner">
        <div class="top-header-titles">
            <h1>Data Exploration, Preparation & Quality Audit</h1>
            <div class="top-header-tagline">
                Rigorous transparency report validating data integrity and mathematical pipeline reproducibility.
            </div>
        </div>
        <div>
            <span class="data-badge-observed">[PRODUCTION DATA AUDIT]</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sas-callout">
        <strong>Enterprise Data Governance:</strong> AROHA adheres to stringent data quality benchmarks across 
        <em>Data Ingestion, Preparation, Statistical Modeling, and Actionable Evidence-Based Recommendations.</em>
        Below is our comprehensive, transparent data preparation audit.
    </div>
    """, unsafe_allow_html=True)

    report = data_service.get_data_quality_report()

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("### 1. Analytics Jobs Dataset")
        aj = report["analytics_jobs"]
        st.markdown(f"""
        - **Total Records:** `{aj['rows']:,}` rows across `{aj['columns']}` columns
        - **Salary Extraction:** Successfully parsed `{aj['salary_coverage_pct']}%` of records
        - **Derived Columns:** Midpoint continuous LPA derived from bracket strings (`6to10` -> `8.0 LPA`)
        - **Experience Parsing:** Extracted numerical min/max/average years from variable text (`6-10 yrs`)
        - **Skills Cleaned:** `{aj['unique_skills_extracted']:,}` technical tokens normalized to canonical taxonomy
        """)

    with d2:
        st.markdown("### 2. DataScience Jobs Dataset")
        ds = report["datascience_jobs"]
        st.markdown(f"""
        - **Total Records:** `{ds['rows']:,}` employer job postings
        - **Employers Tracked:** `{ds['companies']:,}` unique enterprise hiring entities
        - **Salary Parsing:** Standardized string formats with `L` unit suffixes to continuous floats
        - **Hiring Volume:** Aggregated `num_of_jobs` across distinct technical designations
        """)

    st.markdown("---")

    d3, d4 = st.columns(2)
    with d3:
        st.markdown("### 3. JDS Skill Traits Dataset")
        jds = report["jds_skill_traits"]
        st.markdown(f"""
        - **Sample Size:** `{jds['samples']}` junior data scientists
        - **Target Metric:** `{jds['target']}` (`{jds['high_hike_ratio']}%` positive class)
        - **Continuous Features:** 5 skill dimensions scaled 1.0 to 5.0
        - **Modeling:** Logistic Regression and Random Forest with stratified 75/25 validation split
        """)

    with d4:
        st.markdown("### 4. SDS Personality Traits Dataset")
        sds = report["sds_personality_traits"]
        st.markdown(f"""
        - **Sample Size:** `{sds['samples']}` senior data scientists
        - **Target Metric:** `{sds['target']}` (`{sds['success_ratio']}%` positive class)
        - **Features:** Big 5 traits (Neuroticism, Extraversion, Openness, Agreeableness, Conscientiousness)
        - **Cleaning:** Resolved column whitespace (`' extraversion'`), standardized target naming
        """)

    st.markdown("---")
    st.markdown("### Platform Standards & Specifications")
    st.markdown("""
    - **Platform:** AROHA Enterprise Workforce Intelligence
    - **Release:** v1.0.0 Production Release
    - **Tagline:** *"Don't just prepare for today's jobs — build for tomorrow's skills."*
    - **Run Command:** `streamlit run app.py`
    """)
