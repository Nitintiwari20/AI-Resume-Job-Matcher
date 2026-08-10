import re
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.skill_extractor import SkillExtractor

class MatchingEngine:
    def __init__(self, skill_extractor: SkillExtractor = None):
        self.skill_extractor = skill_extractor or SkillExtractor()
        self.tfidf = TfidfVectorizer(stop_words='english')

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        if not text1.strip() or not text2.strip():
            return 0.0
        try:
            vectors = self.tfidf.fit_transform([text1, text2])
            sim = cosine_similarity(vectors[0], vectors[1])[0][0]
            return round(float(sim) * 100, 2)
        except Exception:
            return 0.0

    def extract_years_experience(self, text: str) -> int:
        patterns = [
            r'(\d+)\+?\s*(?:years|yrs)\s*(?:of)?\s*(?:experience|exp)?',
            r'(?:experience|exp)\s*(?:of)?\s*(\d+)\+?\s*(?:years|yrs)'
        ]
        max_exp = 0
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                try:
                    val = int(m)
                    if 0 < val < 30 and val > max_exp:
                        max_exp = val
                except ValueError:
                    pass
        return max_exp

    def match(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        # Extract skills
        resume_skills_list = self.skill_extractor.extract_skills(resume_text)
        jd_skills_list = self.skill_extractor.extract_skills(jd_text)

        resume_skills_set = set(resume_skills_list)
        jd_skills_set = set(jd_skills_list)

        matched_skills = sorted(list(resume_skills_set.intersection(jd_skills_set)))
        missing_skills = sorted(list(jd_skills_set - resume_skills_set))
        extra_skills = sorted(list(resume_skills_set - jd_skills_set))

        # Skill Match Percentage
        if len(jd_skills_set) > 0:
            skill_score = round((len(matched_skills) / len(jd_skills_set)) * 100, 2)
        else:
            skill_score = 100.0 if len(resume_skills_set) > 0 else 0.0

        # Semantic Similarity Score
        semantic_score = self.calculate_semantic_similarity(resume_text, jd_text)

        # Experience level evaluation
        resume_exp = self.extract_years_experience(resume_text)
        jd_exp = self.extract_years_experience(jd_text)
        
        if jd_exp > 0:
            exp_score = min(100.0, round((resume_exp / jd_exp) * 100, 2))
        else:
            exp_score = 90.0

        overall_score = round((0.50 * skill_score) + (0.35 * semantic_score) + (0.15 * exp_score), 2)

        missing_skills_info = []
        for skill_name in missing_skills:
            meta = self.skill_extractor.skill_metadata.get(skill_name, {})
            missing_skills_info.append({
                "name": skill_name,
                "category": meta.get("category", "General"),
                "resources": meta.get("resources", {})
            })

        matched_skills_info = []
        for skill_name in matched_skills:
            meta = self.skill_extractor.skill_metadata.get(skill_name, {})
            matched_skills_info.append({
                "name": skill_name,
                "category": meta.get("category", "General")
            })

        return {
            "overall_score": overall_score,
            "skill_score": skill_score,
            "semantic_score": semantic_score,
            "exp_score": exp_score,
            "experience_details": {
                "resume_exp_years": resume_exp,
                "jd_exp_years": jd_exp
            },
            "skill_gap_matrix": {
                "matched_count": len(matched_skills),
                "missing_count": len(missing_skills),
                "matched_skills": matched_skills_info,
                "missing_skills": missing_skills_info,
                "extra_skills": extra_skills
            }
        }
