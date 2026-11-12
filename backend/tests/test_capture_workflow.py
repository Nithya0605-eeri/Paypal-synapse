from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.payments.checkout_service import execute_procurement_capture


def make_approval(
    status="paypal_order_created",
    payment_status="not_captured",
):
    return SimpleNamespace(
        id=4,
        status=status,
        paypal_order_id="TEST-ORDER-001",
        payment_status=payment_status,
        paypal_capture_id=None,
        paypal_capture_request_id=None,
        amount_cents=11700,
    )


def test_human_confirmation_required():
    db = MagicMock()

    with pytest.raises(ValueError, match="human confirmation"):
        execute_procurement_capture(
            db=db,
            approval_id=4,
            human_confirmed=False,
        )

    db.get.assert_not_called()


def test_missing_approval_rejected():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(ValueError, match="not found"):
        execute_procurement_capture(
            db=db,
            approval_id=4,
            human_confirmed=True,
        )


def test_ineligible_payment_rejected():
    db = MagicMock()
    db.get.return_value = make_approval(
        payment_status="captured"
    )

    with patch(
        "app.payments.checkout_service.capture_paypal_order"
    ) as mock_capture:
        with pytest.raises(ValueError, match="not eligible"):
            execute_procurement_capture(
                db=db,
                approval_id=4,
                human_confirmed=True,
            )

        mock_capture.assert_not_called()


@patch(
    "app.payments.checkout_service.persist_procurement_capture_result"
)
@patch(
    "app.payments.checkout_service.validate_paypal_capture_response"
)
@patch(
    "app.payments.checkout_service.capture_paypal_order"
)
@patch(
    "app.payments.checkout_service.reserve_procurement_capture"
)
@patch(
    "app.payments.checkout_service.validate_paypal_order_for_capture"
)
def test_successful_capture_workflow(
    mock_validate_order,
    mock_reserve,
    mock_capture,
    mock_validate_capture,
    mock_persist,
):
    db = MagicMock()
    db.get.return_value = make_approval()

    mock_reserve.return_value = {
        "paypal_capture_request_id": "TEST-REQUEST-001"
    }

    mock_capture.return_value = {
        "id": "TEST-ORDER-001",
        "status": "COMPLETED",
    }

    mock_validate_capture.return_value = {
        "capture_id": "TEST-CAPTURE-001",
        "status": "COMPLETED",
        "amount_cents": 11700,
        "currency": "USD",
    }

    mock_persist.return_value = {
        "approval_id": 4,
        "paypal_order_id": "TEST-ORDER-001",
        "paypal_capture_id": "TEST-CAPTURE-001",
        "payment_status": "captured",
        "status": "payment_completed",
    }

    result = execute_procurement_capture(
        db=db,
        approval_id=4,
        human_confirmed=True,
    )

    assert result["payment_status"] == "captured"
    assert result["status"] == "payment_completed"
    assert result["paypal_capture_id"] == "TEST-CAPTURE-001"

    mock_validate_order.assert_called_once_with(
        order_id="TEST-ORDER-001",
        expected_amount_cents=11700,
    )

    mock_reserve.assert_called_once_with(
        db=db,
        approval_id=4,
    )

    mock_capture.assert_called_once_with(
        order_id="TEST-ORDER-001",
        request_id="TEST-REQUEST-001",
    )

    mock_validate_capture.assert_called_once_with(
        response=mock_capture.return_value,
        expected_amount_cents=11700,
        expected_order_id="TEST-ORDER-001",
    )

    mock_persist.assert_called_once_with(
        db=db,
        approval_id=4,
        capture_request_id="TEST-REQUEST-001",
        capture_id="TEST-CAPTURE-001",
    )


@patch(
    "app.payments.checkout_service.persist_procurement_capture_result"
)
@patch(
    "app.payments.checkout_service.capture_paypal_order"
)
@patch(
    "app.payments.checkout_service.reserve_procurement_capture"
)
@patch(
    "app.payments.checkout_service.validate_paypal_order_for_capture"
)
def test_uncertain_capture_not_persisted(
    mock_validate_order,
    mock_reserve,
    mock_capture,
    mock_persist,
):
    db = MagicMock()
    db.get.return_value = make_approval()

    mock_reserve.return_value = {
        "paypal_capture_request_id": "TEST-REQUEST-001"
    }

    mock_capture.side_effect = RuntimeError(
        "PayPal capture outcome is uncertain."
    )

    with pytest.raises(RuntimeError, match="uncertain"):
        execute_procurement_capture(
            db=db,
            approval_id=4,
            human_confirmed=True,
        )

    mock_reserve.assert_called_once()
    mock_capture.assert_called_once()
    mock_persist.assert_not_called()


@patch(
    "app.payments.checkout_service.persist_procurement_capture_result"
)
@patch(
    "app.payments.checkout_service.validate_paypal_capture_response"
)
@patch(
    "app.payments.checkout_service.capture_paypal_order"
)
@patch(
    "app.payments.checkout_service.reserve_procurement_capture"
)
@patch(
    "app.payments.checkout_service.validate_paypal_order_for_capture"
)
def test_invalid_capture_not_persisted(
    mock_validate_order,
    mock_reserve,
    mock_capture,
    mock_validate_capture,
    mock_persist,
):
    db = MagicMock()
    db.get.return_value = make_approval()

    mock_reserve.return_value = {
        "paypal_capture_request_id": "TEST-REQUEST-001"
    }

    mock_capture.return_value = {
        "id": "TEST-ORDER-001",
        "status": "COMPLETED",
    }

    mock_validate_capture.side_effect = ValueError(
        "PayPal capture amount mismatch."
    )

    with pytest.raises(ValueError, match="amount mismatch"):
        execute_procurement_capture(
            db=db,
            approval_id=4,
            human_confirmed=True,
        )

    mock_persist.assert_not_called()


@patch(
    "app.payments.checkout_service.capture_paypal_order"
)
@patch(
    "app.payments.checkout_service.reserve_procurement_capture"
)
@patch(
    "app.payments.checkout_service.validate_paypal_order_for_capture"
)
def test_order_validation_failure_prevents_capture(
    mock_validate_order,
    mock_reserve,
    mock_capture,
):
    db = MagicMock()
    db.get.return_value = make_approval()

    mock_validate_order.side_effect = ValueError(
        "PayPal order is not approved for capture."
    )

    with pytest.raises(ValueError, match="not approved"):
        execute_procurement_capture(
            db=db,
            approval_id=4,
            human_confirmed=True,
        )

    mock_reserve.assert_not_called()
    mock_capture.assert_not_called()