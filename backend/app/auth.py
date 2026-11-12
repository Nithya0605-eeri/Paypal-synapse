import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

MERCHANT_API_KEY = os.getenv("MERCHANT_API_KEY")

merchant_key_header = APIKeyHeader(
    name="X-Merchant-API-Key",
    auto_error=False
)


def verify_merchant_api_key(
    api_key: str | None = Security(merchant_key_header)
):
    if not MERCHANT_API_KEY:
        raise RuntimeError(
            "Merchant API key is not configured."
        )

    if not api_key or not secrets.compare_digest(
        api_key,
        MERCHANT_API_KEY
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing merchant API key."
        )

    return True