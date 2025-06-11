import logging

import httpx

from app import settings

recaptcha_http_client = httpx.AsyncClient(
    base_url="https://www.google.com/recaptcha",
)


async def verify_recaptcha(
    *,
    recaptcha_token: str,
    client_ip_address: str,
) -> bool:
    try:
        response = await recaptcha_http_client.post(
            "/api/siteverify",
            data={
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": recaptcha_token,
                "remoteip": client_ip_address,  # https://stackoverflow.com/a/51920956
            },
        )
        response.raise_for_status()
        response_data = response.json()
        if not isinstance(response_data, dict):
            raise ValueError("Invalid response from recaptcha")
        return response_data.get("success", False) is True

    except Exception:
        logging.exception(
            "Failed to verify recaptcha",
            extra={
                "recaptcha_token": recaptcha_token,
                "client_ip_address": client_ip_address,
            },
        )
        return False
