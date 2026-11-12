from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = ROOT / "data" / "historical_sales.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH, parse_dates=["date"])
df = df.sort_values(["product_id", "date"]).reset_index(drop=True)

# Create historical features without using future sales.
grouped = df.groupby("product_id")["units_sold"]

df["lag_1"] = grouped.shift(1)
df["lag_7"] = grouped.shift(7)
df["rolling_7"] = df.groupby("product_id")["units_sold"].transform(
    lambda s: s.shift(1).rolling(7).mean()
)

df["day_of_week"] = df["date"].dt.dayofweek
df["month"] = df["date"].dt.month
df["day_of_year"] = df["date"].dt.dayofyear

df = df.dropna().copy()

features = [
    "product_id",
    "is_weekend",
    "lag_1",
    "lag_7",
    "rolling_7",
    "day_of_week",
    "month",
    "day_of_year",
]

# Chronological split to avoid random train/test leakage.
cutoff = pd.Timestamp("2026-08-01")
train = df[df["date"] < cutoff]
test = df[df["date"] >= cutoff]

X_train = train[features]
y_train = train["units_sold"]
X_test = test[features]
y_test = test["units_sold"]

model = XGBRegressor(
    n_estimators=250,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=2,
)

model.fit(X_train, y_train)

predictions = np.maximum(model.predict(X_test), 0)
baseline = np.maximum(test["lag_7"].to_numpy(), 0)

def evaluate(actual, predicted):
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)
    return {
        "MAE": round(float(mean_absolute_error(actual, predicted)), 3),
        "RMSE": round(
            float(np.sqrt(mean_squared_error(actual, predicted))), 3
        ),
        "WAPE_percent": round(
            float(
                100 * np.sum(np.abs(actual - predicted))
                / max(np.sum(np.abs(actual)), 1)
            ),
            2,
        ),
    }

results = {
    "dataset": "Synthetic historical sales",
    "test_start": str(test["date"].min().date()),
    "test_end": str(test["date"].max().date()),
    "test_rows": len(test),
    "baseline": evaluate(y_test, baseline),
    "xgboost": evaluate(y_test, predictions),
}

joblib.dump(
    {"model": model, "features": features},
    MODEL_DIR / "demand_model.joblib",
)

with open(MODEL_DIR / "metrics.json", "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
print("Model saved successfully!")