
import joblib
import os
import pandas as pd

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "edupulse_model_final.joblib"
)

model_package = joblib.load(MODEL_PATH)

model = model_package["model"]
thresholds = model_package["risk_thresholds"]


def predict_student(
    attendance,
    quiz_1_score_pct,
    quiz_2_score_pct,
    assignment_pct,
    daily_study_hours
):
    features = pd.DataFrame([{
        "attendance": attendance,
        "quiz_1_score_pct": quiz_1_score_pct,
        "quiz_2_score_pct": quiz_2_score_pct,
        "assignment_pct": assignment_pct,
        "daily_study_hours": daily_study_hours
    }])

    predicted_score = model.predict(features)[0]

    if predicted_score < thresholds["high_risk"]:
        risk = "High Risk"
    elif predicted_score < thresholds["medium_risk"]:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    return {
        "predicted_score": round(float(predicted_score), 2),
        "risk": risk
    }
