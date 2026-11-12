from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.ml.predict import predict_next_day
from app.simulation.digital_twin import simulate_demand
from app.optimization.procurement import optimize_procurement


class CommerceState(TypedDict):
    product_id: int
    current_stock: int
    demand_multiplier: float
    days: int
    budget: float
    supplier_offers: list[dict]
    forecast: dict
    simulation: dict
    optimization: dict
    payment_status: str


def inventory_agent(state: CommerceState):
    forecast = predict_next_day(state["product_id"])
    return {"forecast": forecast}


def simulation_agent(state: CommerceState):
    result = simulate_demand(
        product_id=state["product_id"],
        current_stock=state["current_stock"],
        demand_multiplier=state["demand_multiplier"],
        days=state["days"]
    )
    return {"simulation": result}


def procurement_agent(state: CommerceState):
    plan = optimize_procurement(
        offers=state["supplier_offers"],
        required_quantity=state["simulation"]["projected_shortage"],
        budget=state["budget"]
    )
    return {"optimization": plan}


def payment_agent(state: CommerceState):
    return {"payment_status": "awaiting_merchant_approval"}


builder = StateGraph(CommerceState)

builder.add_node("inventory_agent", inventory_agent)
builder.add_node("simulation_agent", simulation_agent)
builder.add_node("procurement_agent", procurement_agent)
builder.add_node("payment_agent", payment_agent)

builder.add_edge(START, "inventory_agent")
builder.add_edge("inventory_agent", "simulation_agent")
builder.add_edge("simulation_agent", "procurement_agent")
builder.add_edge("procurement_agent", "payment_agent")
builder.add_edge("payment_agent", END)

commerce_graph = builder.compile()