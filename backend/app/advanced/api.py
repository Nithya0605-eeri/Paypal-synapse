from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, Supplier, SupplierProduct
from app.ml.predict import predict_next_day
from app.simulation.digital_twin import simulate_demand
from app.optimization.procurement import optimize_procurement
from app.advanced.monte_carlo import simulate_uncertainty
from app.advanced.explainability import explain_forecast
from app.advanced.risk import score_procurement
from app.advanced.evaluation import model_metrics
from app.advanced.gnn import supplier_graph
from app.advanced.llm import explain_recommendation
from app.advanced.chatbot import merchant_chat

router = APIRouter(prefix="/advanced", tags=["Advanced AI - read only"])

def get_product(db, product_id):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    return product

def safe(fn):
    try:
        return fn()
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(400, str(exc)) from exc

@router.get("/monte-carlo/{product_id}")
def monte_carlo(product_id: int, days: int = Query(7,ge=1,le=30), trials: int = Query(1000,ge=100,le=10000), db: Session = Depends(get_db)):
    p = get_product(db,product_id)
    return safe(lambda: simulate_uncertainty(product_id,p.stock_quantity,days,trials))

@router.get("/explain/{product_id}")
def explain(product_id: int, db: Session = Depends(get_db)):
    get_product(db,product_id)
    return safe(lambda: explain_forecast(product_id))

@router.get("/graph/{product_id}")
def graph(product_id: int, db: Session = Depends(get_db)):
    get_product(db,product_id)
    return safe(lambda: supplier_graph(db,product_id))

@router.get("/metrics")
def metrics():
    return model_metrics()

@router.get("/risk/{product_id}")
def risk(product_id: int, budget: float = Query(1000,gt=0), db: Session = Depends(get_db)):
    p = get_product(db,product_id)
    sim = safe(lambda: simulate_demand(product_id,p.stock_quantity,1.5,7))
    offers = db.query(SupplierProduct,Supplier).join(Supplier,SupplierProduct.supplier_id == Supplier.id).filter(SupplierProduct.product_id == product_id).all()
    plan = optimize_procurement([{"supplier_id":s.id,"supplier_name":s.name,"unit_cost":o.unit_cost,"available_quantity":o.available_quantity} for o,s in offers], sim["projected_shortage"],budget)
    reliability = min((s.reliability_score for _,s in offers),default=0)
    return {"plan": plan, "assessment": score_procurement(float(plan["total_cost"]),float(reliability),float(sim["stockout_risk"]),budget)}

@router.get("/agent-explain/{product_id}")
def agent_explain(product_id: int, budget: float = Query(1000,gt=0), db: Session = Depends(get_db)):
    p = get_product(db,product_id)
    forecast = safe(lambda: predict_next_day(product_id))
    sim = safe(lambda: simulate_demand(product_id,p.stock_quantity,1.5,7))
    offers = db.query(SupplierProduct,Supplier).join(Supplier,SupplierProduct.supplier_id == Supplier.id).filter(SupplierProduct.product_id == product_id).all()
    plan = optimize_procurement([{"supplier_id":s.id,"supplier_name":s.name,"unit_cost":o.unit_cost,"available_quantity":o.available_quantity} for o,s in offers],sim["projected_shortage"],budget)
    return explain_recommendation({"forecast":forecast,"simulation":sim,"optimization":plan})

class ChatRequest(BaseModel):
    product_id: int = Field(gt=0)
    question: str = Field(min_length=1,max_length=500)

@router.post("/chat")
def chat(body: ChatRequest, db: Session = Depends(get_db)):
    p = get_product(db,body.product_id)
    return safe(lambda: merchant_chat(body.product_id,body.question,p.stock_quantity))
