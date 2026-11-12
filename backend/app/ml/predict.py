from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = ROOT / "models" / "demand_model.joblib"
DATA_PATH = ROOT / "data" / "historical_sales.csv"


def predict_next_day(product_id: int):
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Train the model first.")

    artifact = joblib.load(MODEL_PATH)
    model = artifact["model"]
    features = artifact["features"]

    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    history = (
        df[df["product_id"] == product_id]
        .sort_values("date")
    )

    if len(history) < 7:
        raise ValueError("Not enough product history.")

    next_date = history["date"].max() + pd.Timedelta(days=1)
    sales = history["units_sold"]

    row = {
        "product_id": product_id,
        "is_weekend": int(next_date.dayofweek >= 5),
        "lag_1": float(sales.iloc[-1]),
        "lag_7": float(sales.iloc[-7]),
        "rolling_7": float(sales.iloc[-7:].mean()),
        "day_of_week": next_date.dayofweek,
        "month": next_date.month,
        "day_of_year": next_date.dayofyear,
    }

    X = pd.DataFrame([row])[features]
    predicted = float(model.predict(X)[0])

    return {
        "product_id": product_id,
        "forecast_date": str(next_date.date()),
        "predicted_units": round(max(predicted, 0), 2),
        "model": "XGBoost",
        "data_source": "synthetic"
    }