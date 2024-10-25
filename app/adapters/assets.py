import logging

import httpx

from app import settings

assets_service_http_client = httpx.AsyncClient(
    base_url=settings.ASSETS_SERVICE_BASE_URL,
    headers={"X-Api-Key": settings.ASSETS_SERVICE_API_KEY},
)


async def delete_avatar_by_user_id(user_id: int) -> None:
    try:
        response = await assets_service_http_client.delete(
            f"/api/v1/users/{user_id}/avatar",
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
    except Exception:
        logging.exception(
            "Failed to delete user avatar by user id",
            extra={"user_id": user_id},
        )
        return None
