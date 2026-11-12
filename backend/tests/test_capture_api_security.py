from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.auth import verify_merchant_api_key
from app.payments import checkout_service


def test_capture_requires_authentication():
    client = TestClient(app)

    response = client.post(
        "/approvals/4/capture",
        json={"human_confirmed": True},
    )

    assert response.status_code in (401, 403)


def test_capture_requires_confirmation():
    fake_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[verify_merchant_api_key] = lambda: True

    try:
        client = TestClient(app)

        response = client.post(
            "/approvals/4/capture",
            json={"human_confirmed": False},
        )

        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


def test_capture_rejects_missing_confirmation():
    fake_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[verify_merchant_api_key] = lambda: True

    try:
        client = TestClient(app)

        response = client.post(
            "/approvals/4/capture",
            json={},
        )

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()

        from unittest.mock import patch


def test_authorized_capture_calls_service():
    fake_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[verify_merchant_api_key] = lambda: True

    try:
        with patch(
            "app.main.execute_procurement_capture"
        ) as mock_capture:

            mock_capture.return_value = {
                "approval_id": 4,
                "paypal_order_id": "TEST-ORDER-001",
                "paypal_capture_id": "TEST-CAPTURE-001",
                "payment_status": "captured",
                "status": "payment_completed",
            }

            client = TestClient(app)

            response = client.post(
                "/approvals/4/capture",
                json={"human_confirmed": True},
            )

            assert response.status_code == 200
            assert response.json()["payment_status"] == "captured"
            assert response.json()["paypal_capture_id"] == "TEST-CAPTURE-001"

            mock_capture.assert_called_once_with(
                db=fake_db,
                approval_id=4,
                human_confirmed=True,
            )

    finally:
        app.dependency_overrides.clear()


def test_capture_service_failure_returns_503():
    fake_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[verify_merchant_api_key] = lambda: True

    try:
        with patch(
            "app.main.execute_procurement_capture"
        ) as mock_capture:

            mock_capture.side_effect = RuntimeError(
                "PayPal capture outcome is uncertain."
            )

            client = TestClient(app)

            response = client.post(
                "/approvals/4/capture",
                json={"human_confirmed": True},
            )

            assert response.status_code == 503
            assert "Do not retry automatically" in response.json()["detail"]

    finally:
        app.dependency_overrides.clear()


def test_capture_invalid_state_returns_409():
    fake_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[verify_merchant_api_key] = lambda: True

    try:
        with patch(
            "app.main.execute_procurement_capture"
        ) as mock_capture:

            mock_capture.side_effect = ValueError(
                "Payment is not eligible for capture."
            )

            client = TestClient(app)

            response = client.post(
                "/approvals/4/capture",
                json={"human_confirmed": True},
            )

            assert response.status_code == 409
            assert "not eligible" in response.json()["detail"]

    finally:
        app.dependency_overrides.clear()