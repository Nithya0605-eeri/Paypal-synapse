import copy

import pytest

from app.payments.paypal_client import validate_paypal_capture_response


ORDER_ID = "TEST-ORDER-001"
AMOUNT_CENTS = 11700


@pytest.fixture
def valid_response():
    return {
        "id": ORDER_ID,
        "status": "COMPLETED",
        "purchase_units": [
            {
                "payments": {
                    "captures": [
                        {
                            "id": "TEST-CAPTURE-001",
                            "status": "COMPLETED",
                            "amount": {
                                "currency_code": "USD",
                                "value": "117.00",
                            },
                        }
                    ]
                }
            }
        ],
    }


def validate(response, order_id=ORDER_ID):
    return validate_paypal_capture_response(
        response,
        AMOUNT_CENTS,
        order_id,
    )


def test_successful_capture(valid_response):
    result = validate(valid_response)

    assert result["capture_id"] == "TEST-CAPTURE-001"
    assert result["status"] == "COMPLETED"
    assert result["amount_cents"] == AMOUNT_CENTS
    assert result["currency"] == "USD"


def test_incorrect_amount_rejected(valid_response):
    response = copy.deepcopy(valid_response)
    response["purchase_units"][0]["payments"]["captures"][0][
        "amount"
    ]["value"] = "100.00"

    with pytest.raises(ValueError, match="amount mismatch"):
        validate(response)


def test_incomplete_capture_rejected(valid_response):
    response = copy.deepcopy(valid_response)
    response["purchase_units"][0]["payments"]["captures"][0][
        "status"
    ] = "PENDING"

    with pytest.raises(ValueError):
        validate(response)


def test_missing_capture_id_rejected(valid_response):
    response = copy.deepcopy(valid_response)
    response["purchase_units"][0]["payments"]["captures"][0][
        "id"
    ] = ""

    with pytest.raises(ValueError):
        validate(response)


def test_incorrect_currency_rejected(valid_response):
    response = copy.deepcopy(valid_response)
    response["purchase_units"][0]["payments"]["captures"][0][
        "amount"
    ]["currency_code"] = "EUR"

    with pytest.raises(ValueError):
        validate(response)


def test_incorrect_order_id_rejected(valid_response):
    with pytest.raises(ValueError, match="order ID mismatch"):
        validate(valid_response, "WRONG-ORDER-999")


def test_missing_order_id_rejected(valid_response):
    with pytest.raises(ValueError):
        validate(valid_response, "")


def test_invalid_expected_amount_rejected(valid_response):
    with pytest.raises(ValueError):
        validate_paypal_capture_response(
            valid_response,
            -100,
            ORDER_ID,
        )


def test_duplicate_captures_rejected(valid_response):
    response = copy.deepcopy(valid_response)
    capture = response["purchase_units"][0]["payments"]["captures"][0]
    response["purchase_units"][0]["payments"]["captures"].append(
        copy.deepcopy(capture)
    )

    with pytest.raises(ValueError):
        validate(response)


def test_incomplete_order_rejected(valid_response):
    response = copy.deepcopy(valid_response)
    response["status"] = "PENDING"

    with pytest.raises(ValueError):
        validate(response)