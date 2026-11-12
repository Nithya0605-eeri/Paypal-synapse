import math

from app.ml.predict import predict_next_day


def simulate_demand(
    product_id: int,
    current_stock: int,
    demand_multiplier: float = 1.0,
    days: int = 7
):
    if current_stock < 0:
        raise ValueError("Current stock cannot be negative.")

    if not 0.1 <= demand_multiplier <= 5.0:
        raise ValueError("Demand multiplier must be between 0.1 and 5.")

    if not 1 <= days <= 30:
        raise ValueError("Simulation days must be between 1 and 30.")

    forecast = predict_next_day(product_id)

    base_daily_demand = forecast["predicted_units"]
    adjusted_daily_demand = base_daily_demand * demand_multiplier

    projected_demand = math.ceil(adjusted_daily_demand * days)
    shortage = max(projected_demand - current_stock, 0)
    remaining_stock = max(current_stock - projected_demand, 0)

    return {
        "product_id": product_id,
        "simulation_days": days,
        "demand_multiplier": demand_multiplier,
        "base_daily_demand": round(base_daily_demand, 2),
        "adjusted_daily_demand": round(adjusted_daily_demand, 2),
        "projected_total_demand": projected_demand,
        "current_stock": current_stock,
        "projected_shortage": shortage,
        "remaining_stock": remaining_stock,
        "stockout_risk": shortage > 0,
        "simulation_type": "scenario_based",
        "data_source": "synthetic"
    }