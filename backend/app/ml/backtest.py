"""Leakage-aware rolling-origin one-day forecasting evaluation.

Run from backend: python -m app.ml.backtest --output ../models/backtest_report.json
This evaluates synthetic data; it does not retrain or overwrite the production model.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[3]
FEATURES = ["product_id", "is_weekend", "lag_1", "lag_7", "rolling_7", "day_of_week", "month", "day_of_year"]


def make_features(raw):
    df = raw.sort_values(["product_id", "date"]).copy()
    group = df.groupby("product_id")["units_sold"]
    df["lag_1"] = group.shift(1)
    df["lag_7"] = group.shift(7)
    df["rolling_7"] = group.transform(lambda s: s.shift(1).rolling(7).mean())
    df["is_weekend"] = (df["date"].dt.dayofweek >= 5).astype(int)
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["day_of_year"] = df["date"].dt.dayofyear
    return df.dropna(subset=FEATURES + ["units_sold"]).sort_values("date").reset_index(drop=True)


def chronological_folds(df, folds=4, horizon_days=30, min_train_days=180):
    dates = pd.DatetimeIndex(sorted(df["date"].unique()))
    if len(dates) < min_train_days + folds * horizon_days:
        raise ValueError("Insufficient history for requested chronological folds")
    first = len(dates) - folds * horizon_days
    for i in range(folds):
        start = dates[first + i * horizon_days]
        end = dates[first + (i + 1) * horizon_days - 1]
        train = df[df["date"] < start]
        test = df[(df["date"] >= start) & (df["date"] <= end)]
        if train.empty or test.empty or train["date"].max() >= test["date"].min():
            raise AssertionError("Invalid chronological fold")
        yield train, test


def score(y, prediction):
    pred = np.maximum(np.asarray(prediction, dtype=float), 0)
    actual = np.asarray(y, dtype=float)
    return {"MAE": round(float(mean_absolute_error(actual, pred)), 4),
            "RMSE": round(float(np.sqrt(mean_squared_error(actual, pred))), 4),
            "WAPE_percent": round(float(100 * np.abs(actual - pred).sum() / max(np.abs(actual).sum(), 1)), 3)}


def evaluate(data_path, folds=4, horizon_days=30):
    raw = pd.read_csv(data_path, parse_dates=["date"])
    df = make_features(raw)
    output = []
    for number, (train, test) in enumerate(chronological_folds(df, folds, horizon_days), 1):
        Xtr, Xte = train[FEATURES], test[FEATURES]
        ytr, yte = train["units_sold"], test["units_sold"]
        models = {
            "mean_baseline": DummyRegressor(strategy="mean"),
            "ridge": Ridge(alpha=10.0),
            "random_forest": RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=2),
            "xgboost": XGBRegressor(n_estimators=250, max_depth=4, learning_rate=0.05, subsample=0.9,
                                     colsample_bytree=0.9, objective="reg:squarederror", random_state=42, n_jobs=2),
        }
        results = {"seasonal_naive_lag7": {"metrics": score(yte, test["lag_7"]), "inference_ms_per_row": 0.0}}
        for name, model in models.items():
            model.fit(Xtr, ytr)
            start = time.perf_counter()
            prediction = model.predict(Xte)
            elapsed_ms = (time.perf_counter() - start) * 1000
            results[name] = {"metrics": score(yte, prediction),
                             "inference_ms_per_row": round(elapsed_ms / len(test), 5)}
        output.append({"fold": number, "train_end": str(train["date"].max().date()),
                       "test_start": str(test["date"].min().date()),
                       "test_end": str(test["date"].max().date()), "test_rows": len(test), "models": results})
    names = list(output[0]["models"])
    summary = {name: {metric: round(float(np.mean([f["models"][name]["metrics"][metric] for f in output])), 4)
                      for metric in ("MAE", "RMSE", "WAPE_percent")} for name in names}
    return {"dataset": "Synthetic historical sales (not live merchant data)",
            "evaluation": "Expanding-window rolling-origin; one-step predictions with observed historical lags",
            "limitations": ["Not recursive multi-day forecasting", "Synthetic data; no external validity claim",
                            "Feature lags use observed prior days; not suitable for unknown future days without updating history",
                            "Inference timing is local and hardware-dependent"],
            "features": FEATURES, "folds": output, "mean_metrics": summary}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "historical_sales.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "models" / "backtest_report.json")
    parser.add_argument("--folds", type=int, default=4)
    parser.add_argument("--horizon-days", type=int, default=30)
    args = parser.parse_args()
    report = evaluate(args.data, args.folds, args.horizon_days)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps({"mean_metrics": report["mean_metrics"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
