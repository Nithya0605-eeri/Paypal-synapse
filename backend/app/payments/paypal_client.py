import os
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path

import httpx
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")

PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com"


def get_paypal_access_token():
    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        raise RuntimeError(
            "PayPal Sandbox credentials are missing."
        )

    try:
        response = httpx.post(
            f"{PAYPAL_BASE_URL}/v1/oauth2/token",
            auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
            headers={"Accept": "application/json"},
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"PayPal authentication failed: HTTP "
            f"{exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Could not connect to PayPal Sandbox."
        ) from exc


def create_paypal_order(
    amount,
    currency="USD",
    request_id=None,
):
    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Invalid payment amount.") from exc

    if not amount.is_finite() or amount <= 0:
        raise ValueError("Payment amount must be positive.")

    if amount != amount.quantize(Decimal("0.01")):
        raise ValueError(
            "Payment amount must have at most 2 decimal places."
        )

    if currency != "USD":
        raise ValueError("Only USD is supported currently.")

    if request_id is not None:
        if (
            not isinstance(request_id, str)
            or not request_id.strip()
            or len(request_id) > 108
        ):
            raise ValueError("Invalid PayPal request ID.")

    access_token = get_paypal_access_token()

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": currency,
                    "value": f"{amount:.2f}",
                },
                "description": (
                    "Synapse AI Commerce procurement order"
                ),
            }
        ],
    }

    try:
        response = httpx.post(
            f"{PAYPAL_BASE_URL}/v2/checkout/orders",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "PayPal-Request-Id": (
                    request_id or str(uuid.uuid4())
                ),
            },
            json=payload,
            timeout=30.0,
        )

        response.raise_for_status()
        order = response.json()

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            "PayPal order creation failed: "
            f"HTTP {exc.response.status_code}. "
            "Verify the outcome before retrying."
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError(
            "PayPal order creation outcome is uncertain. "
            "Do not retry automatically."
        ) from exc

    order_id = order.get("id")

    if not order_id:
        raise RuntimeError(
            "PayPal did not return an order ID."
        )

    approval_url = next(
        (
            link.get("href")
            for link in order.get("links", [])
            if link.get("rel") in ("approve", "payer-action")
        ),
        None,
    )

    return {
        "order_id": order_id,
        "status": order.get("status"),
        "approval_url": approval_url,
    }


def get_paypal_order(order_id: str):
    if not isinstance(order_id, str) or not order_id.strip():
        raise ValueError("PayPal order ID is required.")

    access_token = get_paypal_access_token()

    try:
        response = httpx.get(
            f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            timeout=30.0,
        )

        response.raise_for_status()
        order = response.json()

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            "PayPal order lookup failed: "
            f"HTTP {exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Could not connect to PayPal Sandbox."
        ) from exc

    if order.get("id") != order_id:
        raise RuntimeError(
            "PayPal returned an unexpected order ID."
        )

    return {
        "order_id": order["id"],
        "status": order.get("status"),
        "purchase_units": order.get("purchase_units", []),
        "approval_url": next(
            (
                link.get("href")
                for link in order.get("links", [])
                if link.get("rel") in ("approve", "payer-action")
            ),
            None,
        ),
    }

def validate_paypal_order_for_capture(
    order_id: str,
    expected_amount_cents: int
):
    if not isinstance(order_id, str) or not order_id.strip():
        raise ValueError("PayPal order ID is required.")

    order = get_paypal_order(order_id)

    if order.get("order_id") != order_id:
        raise RuntimeError("PayPal order ID mismatch.")

    if order.get("status") != "APPROVED":
        raise ValueError(
            "PayPal order is not approved for capture."
        )

    purchase_units = order.get("purchase_units", [])

    if len(purchase_units) != 1:
        raise RuntimeError(
            "Expected exactly one purchase unit."
        )
    amount_info = purchase_units[0].get("amount") or {}

    if (
        amount_info.get("currency_code") != "USD"
        or not amount_info.get("value")
    ):
        raise RuntimeError(
            "PayPal order amount or currency is invalid."
        )

    if (
        not isinstance(expected_amount_cents, int)
        or isinstance(expected_amount_cents, bool)
        or expected_amount_cents <= 0
    ):
        raise ValueError("Invalid expected amount.")

    try:
        paypal_amount = Decimal(amount_info["value"])
        paypal_cents = paypal_amount * 100
    except (InvalidOperation, ValueError, TypeError, KeyError):
        raise RuntimeError("Invalid PayPal amount.")

    if paypal_cents != expected_amount_cents:
        raise RuntimeError(
            "PayPal amount does not match approved amount."
        )
    payments = purchase_units[0].get("payments") or {}

    if payments.get("captures") or payments.get("authorizations"):
        raise RuntimeError(
            "Existing payment activity requires reconciliation."
        )

    return order


def capture_paypal_order(order_id: str, request_id: str):
    if not isinstance(order_id, str) or not order_id.strip():
        raise ValueError("PayPal order ID is required.")

    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("Capture request ID is required.")

    access_token = get_paypal_access_token()

    try:
        response = httpx.post(
            f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "PayPal-Request-Id": request_id,
            },
            json={},
            timeout=30.0,
        )

        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"PayPal capture returned HTTP {exc.response.status_code}. "
            "Reconcile the order before retrying."
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError(
            "PayPal capture outcome is uncertain. "
            "Do not retry automatically. Reconciliation is required."
        ) from exc


def validate_paypal_capture_response(
    response: dict,
    expected_amount_cents: int,
    expected_order_id: str,
) -> dict:
    if not isinstance(response, dict):
        raise ValueError("Invalid PayPal capture response.")
    if not isinstance(expected_order_id, str) or not expected_order_id.strip():
        raise ValueError("Expected PayPal order ID is required.")

    if response.get("id") != expected_order_id:
        raise ValueError("PayPal capture order ID mismatch.")

    if (
        not isinstance(expected_amount_cents, int)
        or isinstance(expected_amount_cents, bool)
        or expected_amount_cents <= 0
    ):
        raise ValueError("Invalid expected capture amount.")

    if response.get("status") != "COMPLETED":
        raise ValueError("PayPal order capture is not completed.")

    purchase_units = response.get("purchase_units")

    if not isinstance(purchase_units, list) or len(purchase_units) != 1:
        raise ValueError("Expected exactly one purchase unit.")

    payments = purchase_units[0].get("payments") or {}
    captures = payments.get("captures") or []

    if not isinstance(captures, list) or len(captures) != 1:
        raise ValueError("Expected exactly one PayPal capture.")

    capture = captures[0]

    if capture.get("status") != "COMPLETED":
        raise ValueError("PayPal capture is not completed.")

    capture_id = capture.get("id")

    if not isinstance(capture_id, str) or not capture_id.strip():
        raise ValueError("PayPal capture ID is missing.")

    amount = capture.get("amount") or {}

    if amount.get("currency_code") != "USD":
        raise ValueError("Unexpected PayPal capture currency.")

    try:
        captured_amount = Decimal(str(amount["value"]))
        captured_cents = captured_amount * 100
    except (KeyError, InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid PayPal capture amount.")

    if not captured_cents.is_finite():
        raise ValueError("Invalid PayPal capture amount.")

    if captured_cents != expected_amount_cents:
        raise ValueError("PayPal capture amount mismatch.")

    return {
        "capture_id": capture_id,
        "status": capture["status"],
        "amount_cents": expected_amount_cents,
        "currency": "USD",
    }