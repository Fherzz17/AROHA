"""
NLP Skill Extraction Pipeline for SkillPulse Bharat
Extracts technical competencies, normalizes aliases, and infers job role alignments.
Team: Syntax Society
"""

import re
import time
from typing import List, Dict, Any, Set
from utils.normalizer import ALIAS_MAPPINGS, normalize_skill, CANONICAL_SKILLS
from utils.constants import ROLE_SKILL_PROFILES

class SkillExtractor:
    def __init__(self):
        # Sort phrases by descending length so multi-word expressions like
        # 'retrieval augmented generation' match before 'generation'
        sorted_aliases = sorted(ALIAS_MAPPINGS.keys(), key=lambda x: len(x), reverse=True)
        self.patterns = []
        for alias in sorted_aliases:
            canonical = ALIAS_MAPPINGS[alias]
            # Escape regex chars (like ++, #, /)
            escaped = re.escape(alias)
            # Use non-word boundary checks suitable for symbols like C++, C#, .NET
            if alias in ["c++", "c#", ".net", "go", "r"]:
                pat = re.compile(rf'(?:^|[\s,;/()\[\]]){escaped}(?:[\s,;/()\[\]]|$)', re.IGNORECASE)
            else:
                pat = re.compile(rf'\b{escaped}\b', re.IGNORECASE)
            self.patterns.append((pat, canonical))

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extracts recognized skills from text, normalizes them to canonical forms,
        and scores role alignments.
        """
        start_time = time.perf_counter()
        if not text or not text.strip():
            return {
                "extracted_skills": [],
                "raw_count": 0,
                "role_alignments": [],
                "processing_time_ms": 0.0
            }

        found_skills: Set[str] = set()

        # Step 1: Scan for known alias patterns
        for pattern, canonical in self.patterns:
            if pattern.search(text):
                found_skills.add(canonical)

        # Step 2: Extract explicit comma-separated or bullet point mentions
        lines = re.split(r'[\n\r•\-\*]', text)
        for line in lines:
            line_clean = line.strip()
            if 2 < len(line_clean) < 30:
                normalized = normalize_skill(line_clean)
                if normalized and normalized in CANONICAL_SKILLS:
                    found_skills.add(normalized)

        extracted_list = sorted(list(found_skills))
        
        # Step 3: Compute role alignment scores based on extracted skills
        role_alignments = self._score_role_alignments(extracted_list)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "extracted_skills": extracted_list,
            "raw_count": len(extracted_list),
            "role_alignments": role_alignments,
            "processing_time_ms": elapsed_ms
        }

    def _score_role_alignments(self, skills: List[str]) -> List[Dict[str, Any]]:
        """
        Calculates alignment between extracted skills and predefined career roles.
        """
        if not skills:
            return []

        user_skills_set = set(skills)
        scores = []

        for role_name, profile in ROLE_SKILL_PROFILES.items():
            core_set = set(profile["core"])
            comp_set = set(profile["complementary"])
            emerging_set = set(profile.get("emerging", []))

            core_matches = user_skills_set.intersection(core_set)
            comp_matches = user_skills_set.intersection(comp_set)
            emerging_matches = user_skills_set.intersection(emerging_set)

            # Weighting: Core skills count for 60%, Complementary 25%, Emerging 15%
            core_score = (len(core_matches) / len(core_set)) * 60 if core_set else 0
            comp_score = (len(comp_matches) / len(comp_set)) * 25 if comp_set else 0
            emerging_score = (len(emerging_matches) / len(emerging_set)) * 15 if emerging_set else 0

            total_pct = round(min(100.0, core_score + comp_score + emerging_score), 1)

            scores.append({
                "role": role_name,
                "match_percentage": total_pct,
                "matched_core": list(core_matches),
                "matched_complementary": list(comp_matches),
                "matched_emerging": list(emerging_matches),
                "unmatched_core": list(core_set - user_skills_set)
            })

        scores.sort(key=lambda x: x["match_percentage"], reverse=True)
        return scores[:5]

# Global singleton extractor instance
extractor = SkillExtractor()
