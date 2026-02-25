import os
import joblib
import numpy as np

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
xgb_model_path = os.path.join(base_dir, "models", "xgb_churn_model.pkl")
features_path = os.path.join(base_dir, "models", "churn_features.pkl")

xgb_model = joblib.load(xgb_model_path)
FEATURES = joblib.load(features_path)

def predict_churn(customer_row):
    # Ensure input is a DataFrame with correct feature names if it's a series
    if hasattr(customer_row, 'to_frame'):
        X = customer_row.to_frame().T[FEATURES].values
    elif isinstance(customer_row, dict):
        # Handle dict input from Lab
        X = [[customer_row.get(f, 0) for f in FEATURES]]
    else:
        # Assuming list or array
        X = [customer_row]
        
    prob = xgb_model.predict_proba(X)[0][1]

    if prob >= 0.7:
        risk = "High Risk"
    elif prob >= 0.4:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    return {
        "churn_probability": round(float(prob), 5),
        "churn_risk": risk,
        "p_alive": round(1 - float(prob), 5)
    }