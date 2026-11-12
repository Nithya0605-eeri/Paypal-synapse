from decimal import Decimal
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import update

from app.models import ProcurementApproval
from app.payments.approval_service import (
    get_or_create_paypal_request_id,
)
from app.payments.paypal_client import (
    create_paypal_order,
    get_paypal_order,
    validate_paypal_capture_response,
    validate_paypal_order_for_capture,
    capture_paypal_order,
)


def prepare_procurement_checkout(
    db: Session,
    approval_id: int
):
    approval = db.get(ProcurementApproval, approval_id)

    if approval is None:
        raise ValueError("Procurement request not found.")

    if approval.status != "checkout_pending":
        raise ValueError("Checkout is not pending.")

    if approval.paypal_order_id is not None:
        raise ValueError("PayPal order already exists.")

    if approval.amount_cents <= 0:
        raise ValueError("Invalid procurement amount.")

    request = get_or_create_paypal_request_id(
        db=db,
        approval_id=approval_id
    )

    amount = Decimal(approval.amount_cents) / Decimal(100)

    return {
        "approval_id": approval.id,
        "amount_usd": f"{amount:.2f}",
        "paypal_request_id": request["paypal_request_id"],
        "status": approval.status,
        "payment_status": "not_initiated"
    }

def create_procurement_paypal_order(
    db: Session,
    approval_id: int
):
    checkout = prepare_procurement_checkout(
        db=db,
        approval_id=approval_id
    )
    claim = db.execute(
        update(ProcurementApproval)
        .where(
            ProcurementApproval.id == approval_id,
            ProcurementApproval.status == "checkout_pending",
            ProcurementApproval.paypal_order_id.is_(None)
        )
        .values(status="checkout_processing")
    )

    if claim.rowcount != 1:
        db.rollback()
        raise ValueError(
            "Checkout already started or is unavailable."
        )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    # Use the approved amount from SQLite.
    amount = checkout["amount_usd"]

    # Reuse the persisted idempotency key.
    request_id = checkout["paypal_request_id"]

    # Create a PayPal Sandbox order.
    from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import update

from app.models import ProcurementApproval
from app.payments.approval_service import (
    get_or_create_paypal_request_id,
)
from app.payments.paypal_client import create_paypal_order


def prepare_procurement_checkout(
    db: Session,
    approval_id: int
):
    approval = db.get(ProcurementApproval, approval_id)

    if approval is None:
        raise ValueError("Procurement request not found.")

    if approval.status != "checkout_pending":
        raise ValueError("Checkout is not pending.")

    if approval.paypal_order_id is not None:
        raise ValueError("PayPal order already exists.")

    if approval.amount_cents <= 0:
        raise ValueError("Invalid procurement amount.")

    request = get_or_create_paypal_request_id(
        db=db,
        approval_id=approval_id
    )

    amount = Decimal(approval.amount_cents) / Decimal(100)

    return {
        "approval_id": approval.id,
        "amount_usd": f"{amount:.2f}",
        "paypal_request_id": request["paypal_request_id"],
        "status": approval.status,
        "payment_status": "not_initiated"
    }

def create_procurement_paypal_order(
    db: Session,
    approval_id: int
):
    checkout = prepare_procurement_checkout(
        db=db,
        approval_id=approval_id
    )
    claim = db.execute(
        update(ProcurementApproval)
        .where(
            ProcurementApproval.id == approval_id,
            ProcurementApproval.status == "checkout_pending",
            ProcurementApproval.paypal_order_id.is_(None)
        )
        .values(status="checkout_processing")
    )

    if claim.rowcount != 1:
        db.rollback()
        raise ValueError(
            "Checkout already started or is unavailable."
        )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    # Use the approved amount from SQLite.
    amount = checkout["amount_usd"]

    # Reuse the persisted idempotency key.
    request_id = checkout["paypal_request_id"]

    # Create a PayPal Sandbox order.
    try:
        order = create_paypal_order(
            amount=amount,
            currency="USD",
            request_id=request_id
        )
    except Exception as exc:
        db.rollback()
        raise RuntimeError(
            "PayPal checkout outcome is uncertain. "
            "Do not retry automatically. "
            "Manual reconciliation is required."
        ) from exc
    if not order.get("order_id"):
        raise RuntimeError(
            "PayPal did not return an order ID."
        )

    approval = db.get(
        ProcurementApproval,
        approval_id
    )

    approval.paypal_order_id = order["order_id"]
    approval.status = "paypal_order_created"

    try:
        db.commit()
        db.refresh(approval)
    except Exception:
        db.rollback()
        raise

    return {
        "approval_id": approval.id,
        "paypal_order_id": approval.paypal_order_id,
        "status": approval.status,
        "approval_url": order.get("approval_url"),
        "amount_usd": amount,
        "payment_status": "awaiting_paypal_approval"
    }

def get_procurement_checkout_status(
    db: Session,
    approval_id: int
):
    approval = db.get(ProcurementApproval, approval_id)

    if approval is None:
        raise ValueError("Procurement request not found.")

    if approval.paypal_order_id:
        payment_state = "order_created"
        recovery_action = "use_existing_order"

    elif approval.status == "checkout_processing":
        payment_state = "outcome_unknown"
        recovery_action = "manual_reconciliation_required"

    elif approval.status == "checkout_pending":
        payment_state = "not_initiated_or_unconfirmed"
        recovery_action = "verify_before_checkout"

    else:
        payment_state = "not_ready"
        recovery_action = "review_approval_status"

    return {
        "approval_id": approval.id,
        "checkout_status": approval.status,
        "payment_state": payment_state,
        "paypal_order_exists": bool(approval.paypal_order_id),
        "request_id_stored": bool(approval.paypal_request_id),
        "recovery_action": recovery_action
    }
def get_procurement_checkout_status(
    db: Session,
    approval_id: int
):
    approval = db.get(ProcurementApproval, approval_id)

    if approval is None:
        raise ValueError("Procurement request not found.")

    if approval.paypal_order_id:
        payment_state = "order_created"
        recovery_action = "use_existing_order"

    elif approval.status == "checkout_processing":
        payment_state = "outcome_unknown"
        recovery_action = "manual_reconciliation_required"

    elif approval.status == "checkout_pending":
        payment_state = "not_initiated_or_unconfirmed"
        recovery_action = "verify_before_checkout"

    else:
        payment_state = "not_ready"
        recovery_action = "review_approval_status"

    return {
        "approval_id": approval.id,
        "checkout_status": approval.status,
        "payment_state": payment_state,
        "paypal_order_exists": bool(approval.paypal_order_id),
        "request_id_stored": bool(approval.paypal_request_id),
        "recovery_action": recovery_action
    }

def reserve_procurement_capture(
    db: Session,
    approval_id: int,
):
    capture_request_id = str(uuid.uuid4())

    claim = db.execute(
        update(ProcurementApproval)
        .where(
            ProcurementApproval.id == approval_id,
            ProcurementApproval.status == "paypal_order_created",
            ProcurementApproval.paypal_order_id.is_not(None),
            ProcurementApproval.paypal_capture_id.is_(None),
            ProcurementApproval.paypal_capture_request_id.is_(None),
            ProcurementApproval.payment_status == "not_captured",
            ProcurementApproval.amount_cents > 0,
        )
        .values(
            paypal_capture_request_id=capture_request_id,
            payment_status="capture_reserved",
        )
    )

    if claim.rowcount != 1:
        db.rollback()
        raise ValueError(
            "Capture is unavailable or already reserved. "
            "Review the payment status before retrying."
        )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    approval = db.get(ProcurementApproval, approval_id)

    return {
        "approval_id": approval.id,
        "paypal_order_id": approval.paypal_order_id,
        "amount_cents": approval.amount_cents,
        "paypal_capture_request_id": capture_request_id,
        "payment_status": approval.payment_status,
        "reserved": True,
    }

def persist_procurement_capture_result(
    db: Session,
    approval_id: int,
    capture_request_id: str,
    capture_id: str,
):
    if not isinstance(capture_request_id, str) or not capture_request_id.strip():
        raise ValueError("Capture request ID is required.")

    if not isinstance(capture_id, str) or not capture_id.strip():
        raise ValueError("PayPal capture ID is required.")

    claim = db.execute(
        update(ProcurementApproval)
        .where(
            ProcurementApproval.id == approval_id,
            ProcurementApproval.status == "paypal_order_created",
            ProcurementApproval.payment_status == "capture_reserved",
            ProcurementApproval.paypal_capture_request_id == capture_request_id,
            ProcurementApproval.paypal_capture_id.is_(None),
        )
        .values(
            paypal_capture_id=capture_id,
            payment_status="captured",
            status="payment_completed",
        )
    )

    if claim.rowcount != 1:
        db.rollback()
        raise ValueError(
            "Capture result cannot be persisted. "
            "The reservation may be missing or already completed."
        )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    approval = db.get(ProcurementApproval, approval_id)

    return {
        "approval_id": approval.id,
        "paypal_order_id": approval.paypal_order_id,
        "paypal_capture_id": approval.paypal_capture_id,
        "payment_status": approval.payment_status,
        "status": approval.status,
    }

def execute_procurement_capture(
    db: Session,
    approval_id: int,
    human_confirmed: bool = False,
):
    """
    Execute a human-confirmed PayPal Sandbox capture.

    Never automatically retry uncertain capture outcomes.
    """

    if human_confirmed is not True:
        raise ValueError(
            "Explicit human confirmation is required."
        )

    # Validate the stored approval before any capture attempt.
    approval = db.get(ProcurementApproval, approval_id)

    if approval is None:
        raise ValueError("Procurement approval not found.")

    if (
        approval.status != "paypal_order_created"
        or not approval.paypal_order_id
        or approval.payment_status != "not_captured"
        or approval.paypal_capture_id is not None
        or approval.paypal_capture_request_id is not None
        or approval.amount_cents <= 0
    ):
        raise ValueError(
            "Payment is not eligible for capture."
        )

    order_id = approval.paypal_order_id
    expected_amount_cents = approval.amount_cents

    # Verify PayPal order status and approved amount.
    validate_paypal_order_for_capture(
        order_id=order_id,
        expected_amount_cents=expected_amount_cents,
    )

    # Reserve once in SQLite to block duplicate captures.
    reservation = reserve_procurement_capture(
        db=db,
        approval_id=approval_id,
    )

    capture_request_id = reservation[
        "paypal_capture_request_id"
    ]

    # Capture using the persisted idempotency key.
    # If this fails, leave the reservation in place.
    # Manual reconciliation is required.
    response = capture_paypal_order(
        order_id=order_id,
        request_id=capture_request_id,
    )

    # Never mark the payment complete without validation.
    validated = validate_paypal_capture_response(
        response=response,
        expected_amount_cents=expected_amount_cents,
        expected_order_id=order_id,
    )

    # Persist only the validated capture ID.
    return persist_procurement_capture_result(
        db=db,
        approval_id=approval_id,
        capture_request_id=capture_request_id,
        capture_id=validated["capture_id"],
    )