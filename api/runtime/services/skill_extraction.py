"""
Skill Extraction and NLP Service for SkillPulse Bharat
Extracts technical competencies, normalizes aliases, and aligns with roles.
Team: Syntax Society
"""

from typing import List, Dict, Any, Set
from utils.normalizer import ALIAS_MAPPINGS, normalize_skill, CANONICAL_SKILLS
from services.skill_extractor import SkillExtractor, extractor

def extract_skills_from_text(text: str) -> Dict[str, Any]:
    """Extracts recognized skills and returns alignment with canonical taxonomy."""
    return extractor.extract_skills(text)

def normalize_skill_name(raw_name: str) -> str:
    """Normalizes raw skill name using taxonomy alias dictionary."""
    norm = normalize_skill(raw_name)
    return norm if norm else raw_name.strip().title()
