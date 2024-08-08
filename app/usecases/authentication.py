import logging
from datetime import datetime

from pydantic import BaseModel

from app import security
from app.common_types import UserPrivileges
from app.errors import Error
from app.errors import ErrorCode
from app.repositories import access_tokens
from app.repositories import users


class Identity(BaseModel):
    user_id: int
    username: str
    privileges: UserPrivileges


class AuthorizationGrant(BaseModel):
    unhashed_access_token: str
    identity: Identity
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

    if not security.check_osu_password(
        untrusted_password=password,
        hashed_password=user.hashed_password,
    ):
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Incorrect username or password.",
        )

    if user.privileges & UserPrivileges.USER_PENDING_VERIFICATION != 0:
        return Error(
            error_code=ErrorCode.PENDING_VERIFICATION,
            user_feedback="You must login with the osu! client first.",
        )

    if user.privileges & UserPrivileges.USER_NORMAL == 0:
        return Error(
            error_code=ErrorCode.INSUFFICIENT_PRIVILEGES,
            user_feedback="Insufficient privileges.",
        )

    unhashed_access_token = security.generate_unhashed_access_token()
    hashed_access_token = security.hash_access_token(unhashed_access_token)
    access_token = await access_tokens.create(
        user_id=user.id,
        hashed_access_token=hashed_access_token,
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
        # XXX: intentionally send back the unhashed access token
        unhashed_access_token=unhashed_access_token,
        privileges=access_token.privileges,
        expires_at=None,
        identity=Identity(
            user_id=user.id,
            username=user.username,
            privileges=user.privileges,
        ),
    )


async def logout(
    *,
    user_id: int,
    client_ip_address: str,
    client_user_agent: str,
    trusted_access_token: access_tokens.AccessToken,
) -> None | Error:
    await access_tokens.delete_one(trusted_access_token.hashed_access_token)

    logging.info(
        "User successfully logged out",
        extra={
            "user_id": user_id,
            "client_ip_address": client_ip_address,
            "client_user_agent": client_user_agent,
        },
    )

    return None
