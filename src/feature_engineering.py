import re
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class FeatureEngineer:
    """
    Feature engineering module to convert clean text into numerical features
    for the Machine Learning Model (Skill Score, Semantic Similarity, Exp Fit).
    """
    def __init__(self, vectorizer: TfidfVectorizer = None):
        self.vectorizer = vectorizer or TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)

    def fit_vectorizer(self, corpus: list):
        """Fit TF-IDF vectorizer on training corpus."""
        self.vectorizer.fit(corpus)
        return self.vectorizer

    def compute_tfidf_similarity(self, resume_text: str, jd_text: str) -> float:
        """Compute cosine similarity between resume and job description TF-IDF vectors."""
        if not resume_text.strip() or not jd_text.strip():
            return 0.0
        try:
            vecs = self.vectorizer.transform([resume_text, jd_text])
            sim = cosine_similarity(vecs[0], vecs[1])[0][0]
            return float(sim)
        except Exception:
            return 0.0

    def extract_experience_years(self, text: str) -> int:
        """Extract numeric years of experience using regex patterns."""
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

    def extract_features(self, resume_text: str, jd_text: str, matched_count: int, total_jd_skills: int) -> np.ndarray:
        """
        Construct feature array [skill_ratio, tfidf_sim, exp_ratio] for ML Model prediction.
        """
        skill_ratio = (matched_count / total_jd_skills) if total_jd_skills > 0 else 1.0
        tfidf_sim = self.compute_tfidf_similarity(resume_text, jd_text)
        
        resume_exp = self.extract_experience_years(resume_text)
        jd_exp = self.extract_experience_years(jd_text)
        exp_ratio = (resume_exp / jd_exp) if jd_exp > 0 else 1.0
        exp_ratio = min(1.5, exp_ratio) # bound ratio

        return np.array([[skill_ratio, tfidf_sim, exp_ratio]])
