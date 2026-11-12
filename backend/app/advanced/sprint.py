"""Read-only demo upgrades; no checkout creation or capture endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, Supplier, SupplierProduct, ProcurementApproval
from app.ml.predict import predict_next_day
from app.optimization.procurement import optimize_procurement
from app.advanced.evaluation import model_metrics
from app.advanced.chatbot import merchant_chat
from app.payments.checkout_service import get_procurement_checkout_status
import math

router = APIRouter(prefix="/sprint", tags=["Hackathon Sprint - read only"])

def scenario_data(db, product_id, multiplier, days, budget, delay):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    forecast = predict_next_day(product_id)
    daily = forecast["predicted_units"] * multiplier
    demand = math.ceil(daily * days)
    shortage = max(0, demand - product.stock_quantity)
    offers = db.query(SupplierProduct, Supplier).join(Supplier, SupplierProduct.supplier_id == Supplier.id).filter(SupplierProduct.product_id == product_id).all()
    eligible = [{"supplier_id": s.id, "supplier_name": s.name, "unit_cost": o.unit_cost, "available_quantity": o.available_quantity, "lead_time_days": s.lead_time_days} for o,s in offers if s.lead_time_days + delay <= days]
    plan = optimize_procurement([{k:v for k,v in x.items() if k != "lead_time_days"} for x in eligible], shortage, budget)
    return {"product_id":product_id,"product_name":product.name,"daily_forecast":forecast["predicted_units"],"days":days,"demand_multiplier":multiplier,"supplier_delay_days":delay,"budget":budget,"stock":product.stock_quantity,"projected_demand":demand,"shortage_before_purchase":shortage,"eligible_suppliers":eligible,"procurement":plan,"remaining_shortage":max(0,shortage-plan["total_quantity"]),"data_source":"synthetic","disclaimer":"Scenario-based planning; lead-time eligibility is a simplified assumption. No orders or payments are created."}

@router.get("/scenario/{product_id}")
def scenario(product_id:int, multiplier:float=Query(1.5,ge=0.1,le=5), days:int=Query(7,ge=1,le=30), budget:float=Query(1000,ge=0,le=1000000), delay:int=Query(0,ge=0,le=30), db:Session=Depends(get_db)):
    return scenario_data(db,product_id,multiplier,days,budget,delay)

@router.get("/trace/{product_id}")
def trace(product_id:int, multiplier:float=Query(1.5,ge=0.1,le=5), days:int=Query(7,ge=1,le=30), budget:float=Query(1000,ge=0,le=1000000), delay:int=Query(0,ge=0,le=30), db:Session=Depends(get_db)):
    d=scenario_data(db,product_id,multiplier,days,budget,delay)
    steps=[{"stage":"Forecast","detail":f"{d['daily_forecast']} predicted daily units"},{"stage":"Digital twin","detail":f"{d['projected_demand']} projected units; {d['shortage_before_purchase']} short"},{"stage":"Supplier constraints","detail":f"{len(d['eligible_suppliers'])} suppliers meet simplified delivery window"},{"stage":"Optimization","detail":f"{d['procurement']['total_quantity']} units for ${d['procurement']['total_cost']:.2f}"},{"stage":"Merchant approval","detail":"Required before any checkout; no payment initiated"}]
    return {"steps":steps,"scenario":d,"execution_type":"read-only reconstructed decision trace, not LangGraph execution logs"}

@router.get("/checkout-audit/{approval_id}")
def checkout_audit(approval_id:int, db:Session=Depends(get_db)):
    approval=db.get(ProcurementApproval,approval_id)
    if approval is None:
        raise HTTPException(404,"Approval not found")
    # Existing status function is read-only; never invoke order creation/capture here.
    status=get_procurement_checkout_status(db=db,approval_id=approval_id)
    return {"checkout":status,"approved_amount_usd":round(approval.amount_cents/100,2),"order_id_recorded":bool(approval.paypal_order_id),"capture_id_recorded":bool(approval.paypal_capture_id),"read_only":True,"note":"Status inspection only. Actual Sandbox checkout must be separately merchant-authorized."}

@router.get("/backtest-summary")
def backtest_summary():
    d=model_metrics()
    return {"metrics":d,"evaluation":"existing held-out synthetic dataset","note":"This is a comparative evaluation summary, not new rolling-origin backtesting. Time-series cross-validation remains future work."}

@router.get("/copilot/{product_id}")
def copilot(product_id:int, question:str=Query("Explain the inventory risk",min_length=1,max_length=500),db:Session=Depends(get_db)):
    product=db.get(Product,product_id)
    if product is None:
        raise HTTPException(404,"Product not found")
    return merchant_chat(product_id,question,product.stock_quantity)
