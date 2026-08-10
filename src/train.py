import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from src.preprocessing import TextPreprocessor
from src.skill_extractor import SkillExtractor
from src.feature_engineering import FeatureEngineer

def train_and_save_model():
    """
    Train ML Match Score model and serialize artifacts to models/ directory.
    - models/model.pkl
    - models/vectorizer.pkl
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "job_descriptions.csv")
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)

    print("[INFO] Starting Model Training Pipeline...")
    
    # 1. Load Data
    df = pd.read_csv(data_path)
    job_texts = df["job_description"].tolist()

    # 2. Fit TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)
    vectorizer.fit(job_texts)
    print("[OK] Fitted TfidfVectorizer on corpus.")

    # 3. Create synthetic training dataset of (skill_ratio, tfidf_sim, exp_ratio) -> target match_score
    feature_engineer = FeatureEngineer(vectorizer)

    X_train = []
    y_train = []

    np.random.seed(42)
    for _ in range(500):
        skill_ratio = np.random.uniform(0.1, 1.0)
        tfidf_sim = np.random.uniform(0.05, 0.95)
        exp_ratio = np.random.uniform(0.2, 1.3)

        target_score = (0.50 * skill_ratio * 100) + (0.35 * tfidf_sim * 100) + (0.15 * min(1.0, exp_ratio) * 100)
        noise = np.random.normal(0, 1.5)
        target_score = float(np.clip(target_score + noise, 0.0, 100.0))

        X_train.append([skill_ratio, tfidf_sim, exp_ratio])
        y_train.append(target_score)

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    # 4. Train Random Forest Model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print(f"[OK] Trained RandomForestRegressor Model. R2 Score: {model.score(X_train, y_train):.4f}")

    # 5. Save model.pkl and vectorizer.pkl
    model_path = os.path.join(models_dir, "model.pkl")
    vectorizer_path = os.path.join(models_dir, "vectorizer.pkl")

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    print(f"[SAVED] Trained model -> {model_path}")
    print(f"[SAVED] Vectorizer    -> {vectorizer_path}")
    print("[SUCCESS] Model Training Complete!")

if __name__ == "__main__":
    train_and_save_model()
