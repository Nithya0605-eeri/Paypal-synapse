import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Product, ProcurementApproval
from app.payments.checkout_service import (
    reserve_procurement_capture,
    persist_procurement_capture_result,
)


def test_capture_reservation_prevents_duplicates():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            product = Product(
                name="Capture Test Product",
                category="test",
                price=10.0,
            )
            db.add(product)
            db.flush()

            approval = ProcurementApproval(
                product_id=product.id,
                amount_cents=11700,
                quantity=1,
                status="paypal_order_created",
                paypal_order_id=f"TEST-{uuid.uuid4().hex}",
                payment_status="not_captured",
            )
            db.add(approval)
            db.commit()
            approval_id = approval.id

        with Session(engine) as db:
            result = reserve_procurement_capture(db, approval_id)

            assert result["reserved"] is True
            assert result["payment_status"] == "capture_reserved"
            assert result["paypal_capture_request_id"]

        with Session(engine) as db:
            approval = db.get(ProcurementApproval, approval_id)
            assert approval.paypal_capture_request_id is not None
            assert approval.payment_status == "capture_reserved"

            with pytest.raises(ValueError):
                reserve_procurement_capture(db, approval_id)

        print("TEST PASSED: Duplicate capture reservation blocked.")

    finally:
        engine.dispose()

def test_concurrent_capture_reservation(tmp_path):
    db_path = tmp_path / "capture_concurrency.db"

    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"timeout": 10},
    )

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            product = Product(
                name="Concurrent Capture Test",
                category="test",
                price=10.0,
            )
            db.add(product)
            db.flush()

            approval = ProcurementApproval(
                product_id=product.id,
                amount_cents=11700,
                quantity=1,
                status="paypal_order_created",
                paypal_order_id=f"TEST-{uuid.uuid4().hex}",
                payment_status="not_captured",
            )
            db.add(approval)
            db.commit()
            approval_id = approval.id

        barrier = Barrier(2)

        def attempt_reservation():
            with Session(engine) as db:
                barrier.wait(timeout=10)

                try:
                    result = reserve_procurement_capture(
                        db, approval_id
                    )
                    return ("success", result)
                except ValueError:
                    return ("blocked", None)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(attempt_reservation)
                for _ in range(2)
            ]
            results = [future.result(timeout=20) for future in futures]

        successes = [
            result for status, result in results
            if status == "success"
        ]
        blocked = [
            status for status, _ in results
            if status == "blocked"
        ]

        assert len(successes) == 1
        assert len(blocked) == 1

        with Session(engine) as db:
            approval = db.get(ProcurementApproval, approval_id)

            assert approval.payment_status == "capture_reserved"
            assert (
                approval.paypal_capture_request_id
                == successes[0]["paypal_capture_request_id"]
            )

    finally:
        engine.dispose()

def test_capture_result_persistence():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            product = Product(
                name="Capture Persistence Test",
                category="test",
                price=10.0,
            )
            db.add(product)
            db.flush()

            approval = ProcurementApproval(
                product_id=product.id,
                amount_cents=11700,
                quantity=1,
                status="paypal_order_created",
                paypal_order_id=f"TEST-{uuid.uuid4().hex}",
                payment_status="not_captured",
            )
            db.add(approval)
            db.commit()
            approval_id = approval.id

        with Session(engine) as db:
            reservation = reserve_procurement_capture(
                db, approval_id
            )
            request_id = reservation["paypal_capture_request_id"]

        # An incorrect request ID must be rejected.
        with Session(engine) as db:
            with pytest.raises(ValueError):
                persist_procurement_capture_result(
                    db,
                    approval_id,
                    "incorrect-request-id",
                    "TEST-CAPTURE-001",
                )

        # Simulate persistence after an externally verified capture.
        with Session(engine) as db:
            result = persist_procurement_capture_result(
                db,
                approval_id,
                request_id,
                "TEST-CAPTURE-001",
            )

            assert result["payment_status"] == "captured"
            assert result["status"] == "payment_completed"
            assert result["paypal_capture_id"] == "TEST-CAPTURE-001"

        # A duplicate completion attempt must be rejected.
        with Session(engine) as db:
            with pytest.raises(ValueError):
                persist_procurement_capture_result(
                    db,
                    approval_id,
                    request_id,
                    "TEST-CAPTURE-001",
                )

        with Session(engine) as db:
            approval = db.get(ProcurementApproval, approval_id)
            assert approval.payment_status == "captured"
            assert approval.paypal_capture_id == "TEST-CAPTURE-001"

    finally:
        engine.dispose()