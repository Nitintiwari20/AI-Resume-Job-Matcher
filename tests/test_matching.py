from src.matching_engine import MatchingEngine
from src.ats_checker import ATSChecker
from src.recommender import Recommender
from src.preprocessing import TextPreprocessor
from src.skill_extractor import SkillExtractor

def test_matching_engine():
    engine = MatchingEngine()
    
    resume_text = """
    Full Stack Developer with 4 years experience in Python, React, PostgreSQL, Docker, AWS.
    Built web applications, RESTful APIs, and microservices.
    """

    jd_text = """
    Looking for a Senior Full Stack Engineer with 4+ years of experience.
    Must have strong knowledge of Python, React, PostgreSQL, Docker, Kubernetes, and Redis.
    """

    result = engine.match(resume_text, jd_text)
    assert result["overall_score"] > 50.0

def test_skill_extractor_workflow():
    extractor = SkillExtractor()
    resume_text = "Experienced in Python, React, Docker"
    jd_text = "Needs Python, React, Docker, Kubernetes, AWS"

    gap = extractor.analyze_skill_gap(resume_text, jd_text)
    assert "Python" in gap["strong_skills"]
    assert "React" in gap["strong_skills"]
    assert "Kubernetes" in gap["missing_skills"]
    assert "AWS" in gap["missing_skills"]
    assert len(gap["recommendations"]) == 2

def test_ats_checker():
    checker = ATSChecker()
    preprocessor = TextPreprocessor()
    
    resume_text = """
    Alex Morgan
    alex.morgan@example.com | +1-555-019-2834 | linkedin.com/in/alexmorgan
    
    SUMMARY
    Senior Full Stack Developer with 5+ years of experience.

    TECHNICAL SKILLS
    Python, React, Docker, AWS, PostgreSQL

    WORK EXPERIENCE
    Senior Engineer | TechCorp | 2022 - Present
    - Architected microservices reducing page load time by 42%.
    - Scaled Node.js APIs handling 15,000 requests per minute.
    
    EDUCATION
    BS Computer Science
    """
    
    parsed = {
        "raw_text": resume_text,
        "word_count": len(resume_text.split()),
        "contact": preprocessor.extract_contact_info(resume_text),
        "sections": preprocessor.extract_sections(resume_text)
    }
    ats_result = checker.analyze(parsed)
    assert ats_result["ats_score"] > 60.0

def test_recommender():
    recommender = Recommender()
    bullet_result = recommender.enhance_bullet_point("worked on React UI components")
    assert "Architected & Implemented" in bullet_result["enhanced"] or "Engineered" in bullet_result["enhanced"]
