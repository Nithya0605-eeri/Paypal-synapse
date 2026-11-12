import joblib
import pandas as pd
from app.ml.predict import MODEL_PATH, DATA_PATH

def explain_forecast(product_id: int):
    import shap
    artifact = joblib.load(MODEL_PATH)
    features = artifact["features"]
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    h = df[df.product_id == product_id].sort_values("date")
    if len(h) < 7:
        raise ValueError("Not enough product history")
    d = h.date.max() + pd.Timedelta(days=1)
    s = h.units_sold
    row = {"product_id": product_id, "is_weekend": int(d.dayofweek >= 5),
           "lag_1": float(s.iloc[-1]), "lag_7": float(s.iloc[-7]),
           "rolling_7": float(s.iloc[-7:].mean()), "day_of_week": d.dayofweek,
           "month": d.month, "day_of_year": d.dayofyear}
    x = pd.DataFrame([row])[features]
    explainer = shap.TreeExplainer(artifact["model"])
    explanation = explainer(x)
    return {"product_id": product_id, "base_value": round(float(explanation.base_values[0]), 3),
            "prediction": round(float(artifact["model"].predict(x)[0]), 3),
            "feature_contributions": sorted([{"feature": f, "value": round(float(v), 3),
               "input": float(x.iloc[0][f])} for f, v in zip(features, explanation.values[0])],
               key=lambda item: abs(item["value"]), reverse=True)}
