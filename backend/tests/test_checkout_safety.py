from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Product, ProcurementApproval
from app.payments.checkout_service import (
    create_procurement_paypal_order,
)


def create_test_approval(db):
    """Create a procurement approval in an isolated test database."""
    product = Product(
        name="Test Headphones",
        category="Electronics",
        price=79.99,
        stock_quantity=20,
        reorder_level=10,
    )
    db.add(product)
    db.flush()

    approval = ProcurementApproval(
        product_id=product.id,
        quantity=10,
        amount_cents=39000,
        status="checkout_pending",
    )
    db.add(approval)
    db.commit()

    return approval.id


def test_checkout_timeout():
    with TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=engine)

        try:
            with Session(engine) as db:
                approval_id = create_test_approval(db)

                with patch(
                    "app.payments.checkout_service.create_paypal_order",
                    side_effect=TimeoutError("Simulated timeout"),
                ) as mock_create:

                    with pytest.raises(
                        RuntimeError,
                        match="outcome is uncertain",
                    ):
                        create_procurement_paypal_order(
                            db, approval_id
                        )

                    mock_create.assert_called_once()

                db.expire_all()
                saved = db.get(ProcurementApproval, approval_id)

                assert saved.status == "checkout_processing"
                assert saved.paypal_order_id is None
                assert saved.paypal_request_id is not None

        finally:
            engine.dispose()


def test_successful_checkout():
    with TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=engine)

        try:
            with Session(engine) as db:
                approval_id = create_test_approval(db)

                mock_order = {
                    "order_id": "TEST-SANDBOX-ORDER-123",
                    "approval_url": "https://example.com/test-approval",
                }

                with patch(
                    "app.payments.checkout_service.create_paypal_order",
                    return_value=mock_order,
                ) as mock_create:

                    result = create_procurement_paypal_order(
                        db, approval_id
                    )

                db.expire_all()
                saved = db.get(ProcurementApproval, approval_id)

                assert result["paypal_order_id"] == mock_order["order_id"]
                assert result["status"] == "paypal_order_created"
                assert result["payment_status"] == "awaiting_paypal_approval"

                assert saved.paypal_order_id == mock_order["order_id"]
                assert saved.status == "paypal_order_created"
                assert saved.paypal_request_id is not None

                mock_create.assert_called_once_with(
                    amount="390.00",
                    currency="USD",
                    request_id=saved.paypal_request_id,
                )

        finally:
            engine.dispose()


def test_duplicate_checkout_blocked():
    with TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=engine)

        try:
            with Session(engine) as db:
                approval_id = create_test_approval(db)

                mock_order = {
                    "order_id": "TEST-ORDER-123",
                    "approval_url": "https://example.com/approve",
                }

                with patch(
                    "app.payments.checkout_service.create_paypal_order",
                    return_value=mock_order,
                ) as mock_create:

                    first = create_procurement_paypal_order(
                        db, approval_id
                    )

                    assert first["status"] == "paypal_order_created"

                    with pytest.raises(ValueError):
                        create_procurement_paypal_order(
                            db, approval_id
                        )

                    mock_create.assert_called_once()

                db.expire_all()
                saved = db.get(ProcurementApproval, approval_id)

                assert saved.paypal_order_id == "TEST-ORDER-123"
                assert saved.status == "paypal_order_created"

        finally:
            engine.dispose()


def test_checkout_database_commit_failure():
    with TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=engine)

        try:
            with Session(engine) as db:
                approval_id = create_test_approval(db)

                mock_order = {
                    "order_id": "TEST-ORDER-DB-FAIL",
                    "approval_url": "https://example.com/approve",
                }

                original_commit = db.commit
                commit_count = 0

                def fail_order_save():
                    nonlocal commit_count
                    commit_count += 1

                    # First commit reserves checkout.
                    # Second commit saves the PayPal order.
                    if commit_count == 3:
                        raise RuntimeError(
                            "Simulated database commit failure"
                        )

                    return original_commit()

                with patch(
                    "app.payments.checkout_service.create_paypal_order",
                    return_value=mock_order,
                ) as mock_create:

                    with patch.object(
                        db,
                        "commit",
                        side_effect=fail_order_save,
                    ):
                        with pytest.raises(
                            RuntimeError,
                            match="Simulated database commit failure",
                        ):
                            create_procurement_paypal_order(
                                db, approval_id
                            )

                    mock_create.assert_called_once()

                # Confirm the reservation was preserved.
                db.expire_all()
                saved = db.get(ProcurementApproval, approval_id)

                assert saved is not None
                assert saved.status == "checkout_processing"
                assert saved.paypal_order_id is None
                assert saved.paypal_request_id is not None

                # A second checkout attempt must not call PayPal.
                with patch(
                    "app.payments.checkout_service.create_paypal_order"
                ) as retry_mock:

                    with pytest.raises(ValueError):
                        create_procurement_paypal_order(
                            db, approval_id
                        )

                    retry_mock.assert_not_called()

                # Confirm the database state remains unchanged.
                db.expire_all()
                saved = db.get(ProcurementApproval, approval_id)

                assert saved.status == "checkout_processing"
                assert saved.paypal_order_id is None
                assert saved.paypal_request_id is not None

        finally:
            engine.dispose()