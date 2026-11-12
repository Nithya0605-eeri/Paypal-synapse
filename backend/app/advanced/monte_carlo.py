import numpy as np
from app.ml.predict import predict_next_day

def simulate_uncertainty(product_id: int, stock: int, days: int = 7, trials: int = 1000, volatility: float = 0.25):
    if not 1 <= days <= 30 or not 100 <= trials <= 10000 or not 0 <= volatility <= 2 or stock < 0:
        raise ValueError("Invalid simulation parameters")
    mean = predict_next_day(product_id)["predicted_units"]
    rng = np.random.default_rng(42)
    daily = rng.lognormal(mean=np.log(max(mean, 0.01)) - np.log1p(volatility**2)/2,
                          sigma=np.sqrt(np.log1p(volatility**2)), size=(trials, days))
    totals = daily.sum(axis=1)
    return {"product_id": product_id, "trials": trials, "days": days, "volatility": volatility,
            "stockout_probability": round(float(np.mean(totals > stock)), 4),
            "expected_demand": round(float(totals.mean()), 2),
            "p10_demand": round(float(np.percentile(totals, 10)), 2),
            "p50_demand": round(float(np.percentile(totals, 50)), 2),
            "p90_demand": round(float(np.percentile(totals, 90)), 2),
            "assumptions": "Synthetic lognormal demand uncertainty; not calibrated to real-world volatility"}
