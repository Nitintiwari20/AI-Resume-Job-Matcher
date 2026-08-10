# 🤖 AI Resume Job Matcher & Skill Gap Analyzer

> **A Complete End-to-End Machine Learning & Data Science System for Automated Resume Text Extraction, Skill Parsing, Vector Feature Engineering, ML Match Scoring, and Skill Gap Recommendations.**

---

## 📸 Dashboard Preview

![AI Resume Job Matcher Dashboard](screenshots/Screenshot%202026-08-10%20195843.png)

---

## 📐 Project Directory Architecture

```text
AI-Resume-Job-Matcher/
│
├── data/
│   └── job_descriptions.csv          # Real-world benchmark job descriptions dataset
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb        # Data loading, text normalization & parsing pipeline
│   ├── 02_eda.ipynb                  # Exploratory Data Analysis & skill distribution plots
│   └── 03_model_training.ipynb       # Model training, R2 evaluation & artifact export
│
├── src/
│   ├── preprocessing.py              # Text cleaning, section splitting & contact extraction
│   ├── feature_engineering.py        # TF-IDF vectorization & Cosine Similarity calculation
│   ├── skill_extractor.py            # NLP skill boundary extractor (Strong & Missing skills)
│   └── train.py                      # Production training script for model.pkl & vectorizer.pkl
│
├── models/
│   ├── model.pkl                     # Serialized Random Forest Match Regressor model
│   └── vectorizer.pkl                # Serialized TF-IDF Vectorizer
│
├── api/
│   └── app.py                        # FastAPI production web server & static UI router
│
├── tests/
│   └── test_api.py                   # Automated PyTest test suite (100% passing)
│
├── screenshots/                      # Project dashboard preview & flow charts
│
├── Dockerfile                        # Docker container configuration
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git exclusion rules
└── README.md                         # Documentation & System Guide
```

---

## 🔄 System Flowchart & Pipeline Architecture

```text
                RESUME
                  │
                  ▼
          Text Extraction
                  │
                  ▼
            Data Cleaning
                  │
                  ▼
          Skill Extraction
                  │
          ├──────────────┐
          ▼              ▼
 Resume Features     Job Features
          │              │
          └──────┬───────┘
                 ▼
         Feature Engineering (TF-IDF + Cosine Sim)
                 │
                 ▼
           ML Model (.pkl)
                 │
                 ▼
            Match Score (%)
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
Strong Skills  Missing Skills Recommendation
```

---

## 🛠️ Step-by-Step Pipeline Description

1. **Text Extraction & Cleaning (`src/preprocessing.py`)**:
   - Supports PDF (`pypdf`), Word (`python-docx`), and raw text files.
   - Cleans non-ASCII symbols, normalizes whitespace, extracts contact handles (Email, Phone, LinkedIn, GitHub), and splits sections (*Summary, Skills, Experience, Education*).

2. **Skill Extraction Engine (`src/skill_extractor.py`)**:
   - Parses text against a taxonomy of **500+ technical skills** across Frontend, Backend, AI/ML, Cloud/DevOps, Databases, Security, Mobile, and Soft Skills.
   - Detects **Strong Skills** (present in both resume & target job) and **Missing Skills** (critical gaps).

3. **Feature Engineering (`src/feature_engineering.py`)**:
   - Generates 2-gram TF-IDF vectors using `scikit-learn`.
   - Computes Cosine Similarity between resume text and job description.
   - Synthesizes feature array `[skill_ratio, tfidf_similarity, experience_ratio]` for model inference.

4. **Machine Learning Model (`models/model.pkl`)**:
   - Trained `RandomForestRegressor` model predicting overall job fit score with an $R^2$ score of **0.9966**.
   - Model and TF-IDF vectorizers are exported into `models/model.pkl` and `models/vectorizer.pkl`.

5. **Skill Gap Diagnostics & Learning Recommendations (`src/skill_extractor.py` & `src/recommender.py`)**:
   - Generates a personalized action plan for missing skills complete with recommended courses, documentation links, and hands-on portfolio project ideas.

---

## 🚀 How to Run the Project

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the Machine Learning Model
To retrain the ML model and regenerate serialized artifacts (`model.pkl` & `vectorizer.pkl`):
```bash
python -m src.train
```

### 3. Run Automated Unit Tests
```bash
python -m pytest
```

### 4. Launch the Web Application & REST API
```bash
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```
Open your browser at **[http://localhost:8000](http://localhost:8000)** to interact with the dark-mode web application!

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t ai-resume-matcher .

# Run container
docker run -d -p 8000:8000 ai-resume-matcher
```

---

## 📄 License
MIT License - Open Source & Human-Crafted ML Architecture.
