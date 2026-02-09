



import os
import joblib
import numpy as np
from pathlib import Path

from django.conf import settings
from ml.preprocessing import preprocess_assessment

# Load pipeline ONCE (VERY IMPORTANT)
# --------------------------------------
MODEL_PATH = os.path.join(settings.BASE_DIR, "ml", "logistic_regression.pkl")


if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("ML pipeline not found.")

pipeline = joblib.load(MODEL_PATH)




# -------------------------------------------------
# Core Prediction Function
# -------------------------------------------------

def predict_risk(instance):
    """
    Returns ONLY the predicted class.
    """

   # ✅ Preprocess
    df = preprocess_assessment(instance)

    # Prevent label leakage
    if "y" in df.columns:
        df = df.drop(columns=["y"])

    # ✅ Predict
    pred_class = pipeline.predict(df)[0]

    risk_map = {
        0: "Not at Risk",
        1: "Mild",
        2: "Moderate",
        3: "Severe"
    }

    return risk_map.get(int(pred_class), "Unknown")



# --------------------------------------------------
# Optional (STRONGLY recommended)
# Probability Output
# --------------------------------------------------

def predict_risk_with_confidence(instance):
    """
    Returns:
        (risk_label, confidence_score)
    """

    df = preprocess_assessment(instance)

    prediction = pipeline.predict(df)[0]

    if hasattr(pipeline, "predict_proba"):
        probability = pipeline.predict_proba(df).max()
        probability = round(float(probability), 3)
    else:
        probability = None

    return str(prediction), probability
