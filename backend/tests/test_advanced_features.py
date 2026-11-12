from app.advanced.risk import score_procurement
from app.advanced.evaluation import model_metrics
from app.advanced.monte_carlo import simulate_uncertainty

def test_risk_requires_human():
    result = score_procurement(1200, 0.6, 0.9, 1000)
    assert result["risk_level"] == "high"
    assert result["requires_human_approval"] is True

def test_evaluation():
    assert model_metrics()["xgboost"]["MAE"] < model_metrics()["baseline"]["MAE"]

def test_monte_carlo():
    result = simulate_uncertainty(1, 20, 7, 100)
    assert 0 <= result["stockout_probability"] <= 1
    assert result["p10_demand"] <= result["p90_demand"]
