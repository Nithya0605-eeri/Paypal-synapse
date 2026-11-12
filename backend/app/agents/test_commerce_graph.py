from app.agents.commerce_graph import commerce_graph

initial_state = {
    "product_id": 1,
    "current_stock": 20,
    "demand_multiplier": 2.0,
    "days": 7,
    "budget": 4000.0,
    "supplier_offers": [
        {
            "supplier_id": 1,
            "supplier_name": "TechSupply Co",
            "unit_cost": 42.0,
            "available_quantity": 100
        },
        {
            "supplier_id": 2,
            "supplier_name": "Global Electronics",
            "unit_cost": 39.0,
            "available_quantity": 60
        }
    ]
}

result = commerce_graph.invoke(initial_state)

print("\n=== PAYPAL SYNAPSE AGENT RESULTS ===")
print("Forecast:", result["forecast"])
print("Projected shortage:", result["simulation"]["projected_shortage"])
print("Optimized purchase:", result["optimization"]["purchase_plan"])
print("Total cost:", result["optimization"]["total_cost"])
print("Payment status:", result["payment_status"])