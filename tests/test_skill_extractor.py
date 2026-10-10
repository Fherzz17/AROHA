"""
Unit tests for Skill Extraction and Normalization
Team: Syntax Society
"""

import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.skill_extractor import extractor
from utils.normalizer import normalize_skill

def test_user_requested_example():
    """
    User request test case:
    'Looking for a Python developer with experience in SQL, AWS, Docker and Machine Learning.'
    Expected: Python, SQL, AWS, Docker, Machine Learning
    """
    text = "Looking for a Python developer with experience in SQL, AWS, Docker and Machine Learning."
    result = extractor.extract_skills(text)
    extracted = set(result["extracted_skills"])

    expected = {"Python", "SQL", "AWS", "Docker", "Machine Learning"}
    assert expected.issubset(extracted), f"Expected {expected} to be in {extracted}"

def test_normalization_aliases():
    """
    Verify variations normalize properly:
    'python programming' -> Python
    'Amazon Web Services' -> AWS
    'generative ai' -> Generative AI
    'k8s' -> Kubernetes
    """
    assert normalize_skill("python programming") == "Python"
    assert normalize_skill("Amazon Web Services") == "AWS"
    assert normalize_skill("generative ai") == "Generative AI"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("postgres") == "PostgreSQL"

def test_complex_job_description_extraction():
    text = """
    We need an AI Engineer skilled in Generative AI, RAG, and LLMs.
    Experience with LangChain, PyTorch, and Vector Databases (Pinecone/Chroma) is required.
    Deployments on AWS or GCP using Kubernetes.
    """
    result = extractor.extract_skills(text)
    extracted = set(result["extracted_skills"])

    assert "Generative AI" in extracted
    assert "RAG" in extracted
    assert "LLMs" in extracted
    assert "PyTorch" in extracted
    assert "AWS" in extracted or "GCP" in extracted
    assert "Kubernetes" in extracted

def test_role_alignment_scoring():
    text = "Hiring a Data Analyst with solid SQL, Power BI, Excel, and Statistics skills."
    result = extractor.extract_skills(text)
    alignments = result["role_alignments"]

    assert len(alignments) > 0
    top_role = alignments[0]["role"]
    assert top_role == "Data Analyst"
