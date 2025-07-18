from fastapi import APIRouter
from fastapi import Cookie
from fastapi import Header
from fastapi import Response
from pydantic import BaseModel

from app.api import authorization
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
        value=response.unhashed_access_token,
        expires=60 * 60 * 24 * 30,
        domain="akatsuki.gg",
        secure=True,
        httponly=True,
        samesite="none",
    )
    return http_response


@router.post("/public/api/v1/logout")
async def logout(
    client_ip_address: str = Header(..., alias="X-Real-IP"),
    client_user_agent: str = Header(..., alias="User-Agent"),
    user_access_token: str = Cookie(..., alias="X-Ripple-Token", strict=True),
) -> Response:
    trusted_access_token = await authorization.authorize_request(
        user_access_token=user_access_token,
        expected_user_id=None,
    )
    if isinstance(trusted_access_token, Error):
        return JSONResponse(
            content=trusted_access_token.model_dump(),
            status_code=map_error_code_to_http_status_code(
                trusted_access_token.error_code,
            ),
        )

    response = await authentication.logout(
        client_ip_address=client_ip_address,
        client_user_agent=client_user_agent,
        trusted_access_token=trusted_access_token,
    )
    if isinstance(response, Error):
        return JSONResponse(
            content=response.model_dump(),
            status_code=map_error_code_to_http_status_code(response.error_code),
        )

    http_response = Response(status_code=204)
    http_response.delete_cookie(
        "X-Ripple-Token",
        domain="akatsuki.gg",
        secure=True,
        httponly=True,
        samesite="none",
    )
    return http_response


class InitializePasswordResetRequest(BaseModel):
    username: str
    recaptcha_token: str


@router.post("/public/api/v1/init-password-reset")
async def initialize_password_reset(
    args: InitializePasswordResetRequest,
    client_ip_address: str = Header(..., alias="X-Real-IP"),
    client_user_agent: str = Header(..., alias="User-Agent"),
) -> Response:
    response = await authentication.initialize_password_reset(
        username=args.username,
        recaptcha_token=args.recaptcha_token,
        client_ip_address=client_ip_address,
        client_user_agent=client_user_agent,
    )
    if isinstance(response, Error):
        return JSONResponse(
            content=response.model_dump(),
            status_code=map_error_code_to_http_status_code(response.error_code),
        )

    return Response(status_code=204)


class VerifyPasswordResetRequest(BaseModel):
    hashed_password_reset_token: str
    new_password: str


@router.post("/public/api/v1/verify-password-reset")
async def verify_password_reset(
    args: VerifyPasswordResetRequest,
    client_ip_address: str = Header(..., alias="X-Real-IP"),
    client_user_agent: str = Header(..., alias="User-Agent"),
) -> Response:
    response = await authentication.verify_password_reset(
        hashed_password_reset_token=args.hashed_password_reset_token,
        new_password=args.new_password,
        client_ip_address=client_ip_address,
        client_user_agent=client_user_agent,
    )
    if isinstance(response, Error):
        return JSONResponse(
            content=response.model_dump(),
            status_code=map_error_code_to_http_status_code(response.error_code),
        )

    return Response(status_code=204)
