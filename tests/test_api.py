from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_api_presets():
    response = client.get("/api/presets")
    assert response.status_code == 200
    data = response.json()
    assert "sample_resumes" in data
    assert "sample_jds" in data
    assert "skills_db" in data

def test_api_analyze_match():
    payload = {
        "resume_text": "Experienced Python and React developer with PostgreSQL experience.",
        "jd_text": "Seeking Python, React, and Kubernetes developer."
    }
    response = client.post("/api/analyze-match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "match_analysis" in data
    assert data["match_analysis"]["overall_score"] > 0
    assert "strong_skills" in data
    assert "missing_skills" in data
    assert "learning_roadmap" in data

def test_api_batch_match():
    payload = {
        "jd_text": "Need Python, React, PostgreSQL",
        "resumes": [
            {"id": "1", "name": "Alice", "text": "Python React PostgreSQL developer"},
            {"id": "2", "name": "Bob", "text": "Java C++ developer"}
        ]
    }
    response = client.post("/api/batch-match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_count"] == 2
    assert data["leaderboard"][0]["name"] == "Alice"

def test_api_enhance_bullet():
    payload = {"bullet": "worked on website UI"}
    response = client.post("/api/enhance-bullet", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "enhanced" in data
