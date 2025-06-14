import logging

from fastapi import APIRouter
from fastapi import Cookie
from fastapi import Header
from fastapi import Response
from pydantic import BaseModel

from app.api import authorization
from app.api.responses import JSONResponse
from app.errors import Error
from app.errors import ErrorCode
from app.usecases import users

router = APIRouter(tags=["(Public) Users API"])


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
    ErrorCode.BAD_REQUEST: 400,
    ErrorCode.INCORRECT_CREDENTIALS: 401,
    ErrorCode.INSUFFICIENT_PRIVILEGES: 401,
    ErrorCode.PENDING_VERIFICATION: 401,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.INTERNAL_SERVER_ERROR: 500,
}


class CreateUserRequest(BaseModel):
    username: str
    email_address: str
    password: str
    recaptcha_token: str


@router.post("/public/api/v1/users")
async def create_user(
    args: CreateUserRequest,
    client_ip_address: str = Header(..., alias="X-Real-IP"),
    client_user_agent: str = Header(..., alias="User-Agent"),
) -> Response:
    response = await users.create_and_authenticate_user(
        username=args.username,
        email_address=args.email_address,
        password=args.password,
        recaptcha_token=args.recaptcha_token,
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


class UsernameUpdate(BaseModel):
    new_username: str


@router.put("/public/api/v1/users/{user_id}/username")
async def update_username(
    user_id: int,
    args: UsernameUpdate,
    user_access_token: str = Cookie(..., alias="X-Ripple-Token", strict=True),
) -> Response:
    trusted_access_token = await authorization.authorize_request(
        user_access_token=user_access_token,
        expected_user_id=user_id,
    )
    if isinstance(trusted_access_token, Error):
        return JSONResponse(
            content=trusted_access_token.model_dump(),
            status_code=map_error_code_to_http_status_code(
                trusted_access_token.error_code,
            ),
        )

    response = await users.update_username(user_id, new_username=args.new_username)
    if isinstance(response, Error):
        return JSONResponse(
            content=response.model_dump(),
            status_code=map_error_code_to_http_status_code(response.error_code),
        )

    return Response(status_code=204)


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


@router.put("/public/api/v1/users/{user_id}/password")
async def update_password(
    user_id: int,
    args: PasswordUpdate,
    user_access_token: str = Cookie(..., alias="X-Ripple-Token", strict=True),
) -> Response:
    trusted_access_token = await authorization.authorize_request(
        user_access_token=user_access_token,
        expected_user_id=user_id,
    )
    if isinstance(trusted_access_token, Error):
        return JSONResponse(
            content=trusted_access_token.model_dump(),
            status_code=map_error_code_to_http_status_code(
                trusted_access_token.error_code,
            ),
        )

    response = await users.update_password(
        user_id,
        current_password=args.current_password,
        new_password=args.new_password,
    )
    if isinstance(response, Error):
        return JSONResponse(
            content=response.model_dump(),
            status_code=map_error_code_to_http_status_code(response.error_code),
        )

    return Response(status_code=204)


class EmailAddressUpdate(BaseModel):
    current_password: str
    new_email_address: str


@router.put("/public/api/v1/users/{user_id}/email-address")
async def update_email_address(
    user_id: int,
    args: EmailAddressUpdate,
    user_access_token: str = Cookie(..., alias="X-Ripple-Token", strict=True),
) -> Response:
    trusted_access_token = await authorization.authorize_request(
        user_access_token=user_access_token,
        expected_user_id=user_id,
    )
    if isinstance(trusted_access_token, Error):
        return JSONResponse(
            content=trusted_access_token.model_dump(),
            status_code=map_error_code_to_http_status_code(
                trusted_access_token.error_code,
            ),
        )

    response = await users.update_email_address(
        user_id,
        current_password=args.current_password,
        new_email_address=args.new_email_address,
    )
    if isinstance(response, Error):
        return JSONResponse(
            content=response.model_dump(),
            status_code=map_error_code_to_http_status_code(response.error_code),
        )

    return Response(status_code=204)
