import logging

from fastapi import APIRouter
from fastapi import Cookie
from fastapi import Response
from pydantic import BaseModel

from app.api import authorization
from app.api.responses import JSONResponse
from app.errors import Error
from app.errors import ErrorCode
from app.usecases import users

router = APIRouter(tags=["(Internal) Users API"])


def map_error_code_to_http_status_code(error_code: ErrorCode) -> int:
    status_code = _error_code_to_http_status_code_map.get(error_code)
    if status_code is None:
        logging.warning(
            "No HTTP status code mapping found for error code: %s",
            error_code,
            extra={"error_code": error_code},
        )
        return 500
    return status_code


_error_code_to_http_status_code_map: dict[ErrorCode, int] = {
    ErrorCode.INCORRECT_CREDENTIALS: 401,
    ErrorCode.INSUFFICIENT_PRIVILEGES: 401,
    ErrorCode.PENDING_VERIFICATION: 401,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.INTERNAL_SERVER_ERROR: 500,
}


@router.delete("/api/v1/users/{user_id}")
async def delete_user(user_id: int) -> Response:
    response = await users.delete_one_by_user_id(user_id)
    if isinstance(response, Error):
        return JSONResponse(
            content=response.model_dump(),
            status_code=map_error_code_to_http_status_code(response.error_code),
        )

    return JSONResponse(
        content=response.model_dump(),
        status_code=200,
    )
