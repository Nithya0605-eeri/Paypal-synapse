from fastapi import FastAPI
from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from app.auth import verify_merchant_api_key

from app.payments.approval_service import (
    approve_procurement_request,
    reject_procurement_request,
    reserve_procurement_checkout,
)
from app.payments.checkout_service import (
    create_procurement_paypal_order,
    get_procurement_checkout_status,
    execute_procurement_capture,
)
from app.payments.checkout_service import (
    get_procurement_checkout_status,
)
from app.agents.commerce_graph import commerce_graph
from app.simulation.digital_twin import simulate_demand
from app.optimization.procurement import optimize_procurement
from app.ml.predict import predict_next_day
from app.database import get_db
from app.models import Product, Supplier, SupplierProduct

app = FastAPI(
    title="PayPal Synapse API",
    description="AI-Powered Autonomous Commerce Digital Twin",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to PayPal Synapse",
        "status": "running",
        "project": "Autonomous Commerce Digital Twin"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PayPal Synapse Backend"
    }

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()

    return [
        {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "stock_quantity": product.stock_quantity,
            "reorder_level": product.reorder_level
        }
        for product in products
    ]

@app.get("/suppliers/compare/{product_id}")
def compare_suppliers(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    offers = (
        db.query(SupplierProduct, Supplier)
        .join(
            Supplier,
            SupplierProduct.supplier_id == Supplier.id
        )
        .filter(SupplierProduct.product_id == product_id)
        .order_by(SupplierProduct.unit_cost.asc())
        .all()
    )

    return {
        "product": product.name,
        "suppliers": [
            {
                "supplier_id": supplier.id,
                "supplier_name": supplier.name,
                "unit_cost": offer.unit_cost,
                "available_quantity": offer.available_quantity,
                "lead_time_days": supplier.lead_time_days,
                "reliability_score": supplier.reliability_score
            }
            for offer, supplier in offers
        ]
    }

@app.get("/forecast/{product_id}")
def get_forecast(product_id: int):
    try:
        return predict_next_day(product_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        )

@app.get("/simulate/{product_id}")
def simulate_product_demand(
    product_id: int,
    demand_multiplier: float = 1.0,
    days: int = 7,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    try:
        return simulate_demand(
            product_id=product_id,
            current_stock=product.stock_quantity,
            demand_multiplier=demand_multiplier,
            days=days
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    from fastapi import Query

@app.get("/optimize/{product_id}")
def optimize_product_purchase(
    product_id: int,
    budget: float = Query(4000, ge=0),
    demand_multiplier: float = Query(1.0, ge=0.1, le=5.0),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    simulation = simulate_demand(
        product_id=product_id,
        current_stock=product.stock_quantity,
        demand_multiplier=demand_multiplier,
        days=days
    )

    offers = (
        db.query(SupplierProduct, Supplier)
        .join(
            Supplier,
            SupplierProduct.supplier_id == Supplier.id
        )
        .filter(SupplierProduct.product_id == product_id)
        .all()
    )

    supplier_offers = [
        {
            "supplier_id": supplier.id,
            "supplier_name": supplier.name,
            "unit_cost": offer.unit_cost,
            "available_quantity": offer.available_quantity
        }
        for offer, supplier in offers
    ]

    plan = optimize_procurement(
        offers=supplier_offers,
        required_quantity=simulation["projected_shortage"],
        budget=budget
    )

    return {
        "product_id": product_id,
        "product_name": product.name,
        "simulation": simulation,
        "optimization": plan,
        "payment_status": "not_initiated"
    }

@app.get("/agents/run/{product_id}")
def run_commerce_agents(
    product_id: int,
    budget: float = Query(4000, ge=0),
    demand_multiplier: float = Query(1.0, ge=0.1, le=5.0),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    offers = (
        db.query(SupplierProduct, Supplier)
        .join(
            Supplier,
            SupplierProduct.supplier_id == Supplier.id
        )
        .filter(SupplierProduct.product_id == product_id)
        .all()
    )

    initial_state = {
        "product_id": product_id,
        "current_stock": product.stock_quantity,
        "demand_multiplier": demand_multiplier,
        "days": days,
        "budget": budget,
        "supplier_offers": [
            {
                "supplier_id": supplier.id,
                "supplier_name": supplier.name,
                "unit_cost": offer.unit_cost,
                "available_quantity": offer.available_quantity
            }
            for offer, supplier in offers
        ]
    }

    result = commerce_graph.invoke(initial_state)

    return {
        "product_id": product_id,
        "forecast": result["forecast"],
        "simulation": result["simulation"],
        "optimization": result["optimization"],
        "payment_status": result["payment_status"]
    }

@app.post("/approvals/{approval_id}/approve")
def approve_purchase(
    approval_id: int,
    authorized: bool = Depends(verify_merchant_api_key),
    db: Session = Depends(get_db)
):
    try:
        return approve_procurement_request(
            db=db,
            approval_id=approval_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@app.post("/approvals/{approval_id}/reject")
def reject_purchase(
    approval_id: int,
    authorized: bool = Depends(verify_merchant_api_key),
    db: Session = Depends(get_db)
):
    try:
        return reject_procurement_request(
            db=db,
            approval_id=approval_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@app.post("/approvals/{approval_id}/reserve-checkout")
def reserve_approved_checkout(
    approval_id: int,
    authorized: bool = Depends(verify_merchant_api_key),
    db: Session = Depends(get_db)
):
    try:
        return reserve_procurement_checkout(
            db=db,
            approval_id=approval_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )


@app.post("/approvals/{approval_id}/checkout")
def checkout_approved_purchase(
    approval_id: int,
    authorized: bool = Depends(verify_merchant_api_key),
    db: Session = Depends(get_db)
):
    try:
        return create_procurement_paypal_order(
            db=db,
            approval_id=approval_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )
    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Checkout could not be confirmed. "
                "Do not retry automatically. "
                "Reconciliation may be required."
            )
        )


@app.get("/approvals/{approval_id}/checkout-status")
def read_procurement_checkout_status(
    approval_id: int,
    authorized: bool = Depends(verify_merchant_api_key),
    db: Session = Depends(get_db),
):
    try:
        return get_procurement_checkout_status(
            db=db,
            approval_id=approval_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

        from pydantic import BaseModel, ConfigDict


class CaptureConfirmation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    human_confirmed: bool


@app.post("/approvals/{approval_id}/capture")
def capture_approved_purchase(
    approval_id: int,
    confirmation: CaptureConfirmation,
    authorized: bool = Depends(verify_merchant_api_key),
    db: Session = Depends(get_db),
):
    if confirmation.human_confirmed is not True:
        raise HTTPException(
            status_code=400,
            detail="Explicit human confirmation is required.",
        )

    try:
        return execute_procurement_capture(
            db=db,
            approval_id=approval_id,
            human_confirmed=True,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail=(
                "PayPal capture could not be confirmed. "
                "Do not retry automatically. "
                "Manual reconciliation is required."
            ),
        )