import warnings
from sklearn.exceptions import InconsistentVersionWarning
import joblib
import pandas as pd
from pathlib import Path


# ==========================================
# LOAD MODEL TRIAL
# ==========================================

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)


MODEL_PATH = Path(__file__).resolve().parent / "edupulse_model_trial.joblib"

model_package = joblib.load(MODEL_PATH)

model = model_package["model"]


# ==========================================
# PREDICT STUDENT
# ==========================================

def predict_student(
    attendance,
    quiz_1_score,
    quiz_2_score,
    assignment_score,
    daily_study_hours
):
    # Konversi nilai akademik ke skala 0-100
    quiz_1_score_pct = quiz_1_score / 40 * 100
    quiz_2_score_pct = quiz_2_score / 40 * 100
    assignment_pct = assignment_score / 10 * 100

    # Input harus mengikuti fitur yang digunakan model
    input_data = pd.DataFrame([{
        "attendance": attendance, 
        "quiz_1_score_pct": quiz_1_score_pct,
        "quiz_2_score_pct": quiz_2_score_pct,
        "assignment_pct": assignment_pct,
        "daily_study_hours": daily_study_hours
    }])

    # Prediksi
    predicted_score = model.predict(input_data)[0]

    # Risk berdasarkan threshold akademik
    if predicted_score < 70:
        risk = "High Risk"
    elif predicted_score < 80:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    return {
        "predicted_score": round(float(predicted_score), 2),
        "risk": risk
    }