from fastapi import APIRouter
from fastapi import Header
from fastapi import Response
from pydantic import BaseModel

from app.api.responses import JSONResponse
from app.errors import Error
from app.errors import ErrorCode
from app.usecases import authentication

router = APIRouter(tags=["(Public) Web Authentication API"])


def map_error_code_to_http_status_code(error_code: ErrorCode) -> int:
    return _error_code_to_http_status_code_map[error_code]


_error_code_to_http_status_code_map: dict[ErrorCode, int] = {
    ErrorCode.INCORRECT_CREDENTIALS: 401,
    ErrorCode.INSUFFICIENT_PRIVILEGES: 401,
    ErrorCode.PENDING_VERIFICATION: 401,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.INTERNAL_SERVER_ERROR: 500,
}


class AuthenticationRequest(BaseModel):
    username: str
    password: str


@router.post("/public/api/v1/authenticate")
async def authenticate(
    args: AuthenticationRequest,
    client_ip_address: str = Header(..., alias="X-Real-IP"),
    client_user_agent: str = Header(..., alias="User-Agent"),
) -> Response:
    response = await authentication.authenticate(
        username=args.username,
        password=args.password,
        client_ip_address=client_ip_address,
        client_user_agent=client_user_agent,
    )
    if isinstance(response, Error):
        return JSONResponse(
            content=response.model_dump(),
            status_code=map_error_code_to_http_status_code(response.error_code),
        )

    http_response = JSONResponse(
        content=response.identity.model_dump(),
        status_code=200,
    )
    http_response.set_cookie(
        "X-Ripple-Token",
        value=response.access_token,
        domain="akatsuki.gg",
        secure=True,
        httponly=True,
        samesite="strict",
    )
    return http_response
