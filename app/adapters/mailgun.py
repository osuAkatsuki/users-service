import logging

import httpx

from app import settings

mailgun_http_client = httpx.AsyncClient(
    base_url=settings.MAILGUN_BASE_URL,
    auth=httpx.BasicAuth("api", settings.MAILGUN_API_KEY),
)


async def send_html_email(*, to_address: str, subject: str, message: str) -> None:
    try:
        response = await mailgun_http_client.post(
            f"/v3/{settings.MAILGUN_DOMAIN_NAME}/messages",
            data={
                "from": f"Akatsuki <noreply@{settings.MAILGUN_DOMAIN_NAME}>",
                "to": to_address,
                "subject": subject,
                "html": message,
            },
        )
        response.raise_for_status()
    except Exception:
        logging.exception(
            "Failed to send email",
            extra={
                "to_address": to_address,
                "subject": subject,
                "html_content": message,
            },
        )
        return None
