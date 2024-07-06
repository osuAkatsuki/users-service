from datetime import datetime
import logging
from app import logger, security
from app.common_types import UserPrivileges
from app.repositories import access_tokens, users
import app.state
from app.errors import Error, ErrorCode
from pydantic import BaseModel


class AuthorizationGrant(BaseModel):
    access_token: str
    privileges: UserPrivileges
    expires_at: datetime | None


async def authenticate(
    *,
    username: str,
    password: str,
    client_ip_address: str,
    client_user_agent: str,
) -> AuthorizationGrant | Error:
    user = await users.fetch_one_by_username(username)
    if user is None:
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Incorrect username or password.",
        )

    if not security.check_password(password, user.hashed_password):
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Incorrect username or password.",
        )

    # TODO: check for & deny pending verification

    if user.privileges & UserPrivileges.USER_NORMAL == 0:
        return Error(
            error_code=ErrorCode.INSUFFICIENT_PRIVILEGES,
            user_feedback="Insufficient privileges.",
        )

    access_token = await access_tokens.create(
        user_id=user.id,
        access_token=security.generate_access_token(),
    )

    # TODO: log amplitude web_login event

    logging.info(
        "User successfully authenticated",
        extra={
            "username": username,
            "user_id": user.id,
            "client_ip_address": client_ip_address,
            "client_user_agent": client_user_agent,
        },
    )

    return AuthorizationGrant(
        access_token=access_token.access_token,
        privileges=access_token.privileges,
        expires_at=None,
    )
