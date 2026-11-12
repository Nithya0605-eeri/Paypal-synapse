import json
from app.ml.predict import ROOT

def model_metrics():
    with (ROOT / "models" / "metrics.json").open() as f:
        metrics = json.load(f)
    baseline = metrics["baseline"]
    model = metrics["xgboost"]
    return {**metrics, "mae_improvement_percent": round(100*(baseline["MAE"]-model["MAE"])/baseline["MAE"], 2),
            "caution": "Evaluation uses held-out synthetic sales data, not live merchant data"}
