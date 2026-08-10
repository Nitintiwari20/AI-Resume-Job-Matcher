import json
import os
import re
from typing import Dict, Any, List, Set

class SkillExtractor:
    """
    NLP Skill Extractor module.
    Analyzes resume and job description text against skills taxonomy
    to return Strong Skills (Matched), Missing Skills (Gap), and Actionable Recommendations.
    """
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "data", "skills_db.json")

        self.db_path = db_path
        self.skills_db = self._load_db()
        self.alias_map, self.skill_metadata = self._build_alias_map()

    def _load_db(self) -> Dict[str, Any]:
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"categories": {}}

    def _build_alias_map(self):
        alias_map = {}
        skill_metadata = {}

        for category, skills in self.skills_db.get("categories", {}).items():
            for skill in skills:
                canonical = skill["name"]
                resources = skill.get("resources", {})
                skill_metadata[canonical] = {
                    "category": category,
                    "resources": resources
                }

                alias_map[canonical.lower()] = canonical
                for alias in skill.get("aliases", []):
                    alias_map[alias.lower()] = canonical

        return alias_map, skill_metadata

    def extract_skills(self, text: str) -> List[str]:
        """Extract present skills from raw text using boundary matching."""
        if not text:
            return []
        text_lower = f" {text.lower()} "
        found: Set[str] = set()

        for alias, canonical in self.alias_map.items():
            escaped = re.escape(alias)
            if alias in ["c++", "cpp"]:
                pattern = r'(?:\b|(?<=\s))(?:c\+\+|cpp)(?=\b|[\s,.;:])'
            elif alias in ["c#", "csharp"]:
                pattern = r'(?:\b|(?<=\s))(?:c\#|csharp)(?=\b|[\s,.;:])'
            else:
                pattern = r'(?:\b|(?<=\s))' + escaped + r'(?=\b|[\s,.;:])'

            if re.search(pattern, text_lower, re.IGNORECASE):
                found.add(canonical)

        return sorted(list(found))

    def analyze_skill_gap(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Extract Strong Skills, Missing Skills, and Recommendations according to workflow requirement:
        RESUME -> Skill Extraction -> Strong Skills / Missing Skills / Recommendation
        """
        resume_skills = set(self.extract_skills(resume_text))
        jd_skills = set(self.extract_skills(jd_text))

        strong_skills = sorted(list(resume_skills.intersection(jd_skills)))
        missing_skills = sorted(list(jd_skills - resume_skills))
        extra_skills = sorted(list(resume_skills - jd_skills))

        # Generate Actionable Learning Recommendations for missing skills
        recommendations = []
        for idx, skill in enumerate(missing_skills, 1):
            meta = self.skill_metadata.get(skill, {})
            category = meta.get("category", "General Tech")
            res = meta.get("resources", {})

            course = res.get("course", f"Complete {skill} Developer Guide")
            doc_link = res.get("doc", f"https://www.google.com/search?q={skill}+documentation")
            project_idea = f"Build a practical hands-on mini application demonstrating {skill} implementation."

            recommendations.append({
                "id": idx,
                "missing_skill": skill,
                "category": category,
                "priority": "High Priority" if idx <= 3 else "Recommended",
                "recommended_course": course,
                "documentation_url": doc_link,
                "suggested_project": project_idea
            })

        return {
            "strong_skills": strong_skills,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills,
            "recommendations": recommendations
        }
