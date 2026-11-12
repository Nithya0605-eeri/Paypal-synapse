from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models import Product, ProcurementApproval
import uuid
from sqlalchemy import update


def create_procurement_request(
    db: Session,
    product_id: int,
    quantity: int,
    amount_cents: int
):
    if quantity <= 0:
        raise ValueError("Quantity must be positive.")

    if amount_cents <= 0:
        raise ValueError("Amount must be positive.")

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise ValueError("Product not found.")

    approval = ProcurementApproval(
        product_id=product_id,
        quantity=quantity,
        amount_cents=amount_cents,
        status="pending"
    )

    db.add(approval)

    try:
        db.commit()
        db.refresh(approval)
    except Exception:
        db.rollback()
        raise

    return {
        "approval_id": approval.id,
        "product_id": approval.product_id,
        "quantity": approval.quantity,
        "amount_cents": approval.amount_cents,
        "status": approval.status,
        "paypal_order_id": approval.paypal_order_id
    }

def reject_procurement_request(
    db: Session,
    approval_id: int
):
    approval = db.query(ProcurementApproval).filter(
        ProcurementApproval.id == approval_id
    ).first()

    if approval is None:
        raise ValueError("Approval request not found.")

    if approval.status != "pending":
        raise ValueError(
            "Only pending requests can be rejected."
        )

    approval.status = "rejected"

    try:
        db.commit()
        db.refresh(approval)
    except Exception:
        db.rollback()
        raise

    return {
        "approval_id": approval.id,
        "status": approval.status,
        "paypal_order_id": approval.paypal_order_id
    }

def approve_procurement_request(
    db: Session,
    approval_id: int
):
    approval = db.query(ProcurementApproval).filter(
        ProcurementApproval.id == approval_id
    ).first()

    if approval is None:
        raise ValueError("Approval request not found.")

    if approval.status != "pending":
        raise ValueError("Only pending requests can be approved.")

    approval.status = "approved"
    approval.approved_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(approval)
    except Exception:
        db.rollback()
        raise

    return {
        "approval_id": approval.id,
        "status": approval.status,
        "amount_cents": approval.amount_cents,
        "paypal_order_id": approval.paypal_order_id
    }

def get_approved_procurement_request(
    db: Session,
    approval_id: int
):
    approval = db.query(ProcurementApproval).filter(
        ProcurementApproval.id == approval_id
    ).first()

    if approval is None:
        raise ValueError("Procurement request not found.")

    if approval.status != "approved":
        raise ValueError(
            "Procurement request requires merchant approval."
        )

    if approval.paypal_order_id is not None:
        raise ValueError(
            "A PayPal order already exists for this request."
        )

    if approval.amount_cents <= 0:
        raise ValueError("Invalid procurement amount.")

    return {
        "approval_id": approval.id,
        "product_id": approval.product_id,
        "amount_cents": approval.amount_cents,
        "amount_usd": f"{approval.amount_cents / 100:.2f}",
        "quantity": approval.quantity,
        "status": approval.status
    }

from sqlalchemy import update


def reserve_procurement_checkout(
    db: Session,
    approval_id: int
):
    result = db.execute(
        update(ProcurementApproval)
        .where(
            ProcurementApproval.id == approval_id,
            ProcurementApproval.status == "approved",
            ProcurementApproval.paypal_order_id.is_(None),
            ProcurementApproval.amount_cents > 0
        )
        .values(status="checkout_pending")
    )

    if result.rowcount != 1:
        db.rollback()
        raise ValueError(
            "Request is not approved or checkout already started."
        )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    approval = db.get(ProcurementApproval, approval_id)

    return {
        "approval_id": approval.id,
        "amount_cents": approval.amount_cents,
        "status": approval.status
    }

def get_or_create_paypal_request_id(
    db: Session,
    approval_id: int
):
    new_request_id = str(uuid.uuid4())

    try:
        db.execute(
            update(ProcurementApproval)
            .where(
                ProcurementApproval.id == approval_id,
                ProcurementApproval.status == "checkout_pending",
                ProcurementApproval.paypal_order_id.is_(None),
                ProcurementApproval.paypal_request_id.is_(None)
            )
            .values(paypal_request_id=new_request_id)
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    approval = db.get(ProcurementApproval, approval_id)

    if approval is None:
        raise ValueError("Procurement request not found.")

    if approval.status != "checkout_pending":
        raise ValueError("Checkout is not pending.")

    if approval.paypal_order_id is not None:
        raise ValueError("PayPal order already exists.")

    if not approval.paypal_request_id:
        raise ValueError("PayPal request ID is unavailable.")

    return {
        "approval_id": approval.id,
        "paypal_request_id": approval.paypal_request_id,
        "status": approval.status
    }
