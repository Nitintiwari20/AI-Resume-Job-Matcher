import pytest
from src.preprocessing import TextPreprocessor

def test_preprocessor_contact_extraction():
    preprocessor = TextPreprocessor()
    sample_text = """
    Jane Doe
    Email: jane.doe@example.com
    Phone: +1-555-123-4567
    LinkedIn: linkedin.com/in/janedoe
    GitHub: github.com/janedoe
    """
    contact = preprocessor.extract_contact_info(sample_text)
    assert contact["email"] == "jane.doe@example.com"
    assert contact["phone"] == "+1-555-123-4567"
    assert "linkedin.com/in/janedoe" in contact["linkedin"]
    assert "github.com/janedoe" in contact["github"]

def test_preprocessor_sections():
    preprocessor = TextPreprocessor()
    sample_text = """
    Jane Doe
    
    SUMMARY
    Experienced developer with 4 years in software engineering.

    SKILLS
    Python, React, PostgreSQL, Docker

    EXPERIENCE
    Software Engineer at Acme Corp (2020-2024).
    Built web applications using Python and React.

    EDUCATION
    BS in Computer Science
    """
    sections = preprocessor.extract_sections(sample_text)
    assert "Experienced developer" in sections["summary"]
    assert "Python, React" in sections["skills"]
    assert "Acme Corp" in sections["experience"]
    assert "Computer Science" in sections["education"]
