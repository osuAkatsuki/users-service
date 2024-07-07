from fastapi import APIRouter
from fastapi import Response

from app.api.responses import JSONResponse
from app.errors import Error
from app.errors import ErrorCode
from app.usecases import users

router = APIRouter(tags=["(Public) Users API"])


def map_error_code_to_http_status_code(error_code: ErrorCode) -> int:
    return _error_code_to_http_status_code_map[error_code]


_error_code_to_http_status_code_map: dict[ErrorCode, int] = {
    ErrorCode.INCORRECT_CREDENTIALS: 401,
    ErrorCode.INSUFFICIENT_PRIVILEGES: 401,
    ErrorCode.PENDING_VERIFICATION: 401,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.INTERNAL_SERVER_ERROR: 500,
}


@router.get("/public/api/v1/users/{user_id}")
async def get_user(user_id: int) -> Response:
    response = await users.fetch_one_by_user_id(user_id)
    if isinstance(response, Error):
        return JSONResponse(
            content=response.model_dump(),
            status_code=map_error_code_to_http_status_code(response.error_code),
        )

    return JSONResponse(
        content=response.model_dump(),
        status_code=200,
    )
