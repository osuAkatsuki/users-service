import logging
from datetime import datetime

from pydantic import BaseModel

from app import security
from app.adapters import mailgun
from app.common_types import UserPrivileges
from app.errors import Error
from app.errors import ErrorCode
from app.repositories import access_tokens
from app.repositories import password_reset_tokens
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

    unhashed_access_token = security.generate_unhashed_secure_token()
    hashed_access_token = security.hash_secure_token(unhashed_access_token)
    access_token = await access_tokens.create(
        user_id=user.id,
        hashed_access_token=hashed_access_token,
    )

    # TODO: log amplitude web_login event

    logging.info(
        "User successfully authenticated",
        extra={
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
    client_ip_address: str,
    client_user_agent: str,
    trusted_access_token: access_tokens.AccessToken,
) -> None | Error:
    await access_tokens.delete_one(trusted_access_token.hashed_access_token)

    logging.info(
        "User successfully logged out",
        extra={
            "user_id": trusted_access_token.user_id,
            "client_ip_address": client_ip_address,
            "client_user_agent": client_user_agent,
        },
    )

    return None


async def initialize_password_reset(
    *,
    username: str,
    client_ip_address: str,
    client_user_agent: str,
) -> None | Error:
    user = await users.fetch_one_by_username(username)
    if user is None:
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Incorrect username.",
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

    unhashed_password_reset_token = security.generate_unhashed_secure_token()
    hashed_password_reset_token = security.hash_secure_token(
        unhashed_password_reset_token,
    )
    password_reset_token = await password_reset_tokens.create(
        username=user.username,
        hashed_token=hashed_password_reset_token,
    )

    # TODO: log amplitude (web_)password_reset event

    logging.info(
        "User initiated password reset process",
        extra={
            "username": username,
            "user_id": user.id,
            "client_ip_address": client_ip_address,
            "client_user_agent": client_user_agent,
        },
    )

    await mailgun.send_email(
        to_address=user.email,
        subject="Akatsuki Password Reset",
        message=(
            f"Hello {user.username},<br /><br />"
            "Someone (<i>which we really hope was you</i>), requested a password "
            "reset for your Akatsuki account. In case it was you, please "
            f"<a href='https://next.akatsuki.gg/reset-password?token={password_reset_token.hashed_token}'>click here</a> "
            "to reset your password on Akatsuki.<br />"
            "Otherwise, silently ignore this email.<br /><br />"
            "- The Akatsuki Team"
        ),
    )

    return None


async def verify_password_reset(
    *,
    hashed_password_reset_token: str,
    new_password: str,
    client_ip_address: str,
    client_user_agent: str,
) -> None | Error:
    password_reset_token = await password_reset_tokens.fetch_one(
        hashed_password_reset_token,
    )
    if password_reset_token is None:
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Invalid password reset token.",
        )

    user = await users.fetch_one_by_username(password_reset_token.username)
    if user is None:
        return Error(
            error_code=ErrorCode.NOT_FOUND,
            user_feedback="User not found.",
        )

    hashed_new_password = security.hash_osu_password(new_password)
    await users.update_password(
        user_id=user.id,
        new_hashed_password=hashed_new_password,
    )

    await password_reset_tokens.delete_one(password_reset_token.hashed_token)

    logging.info(
        "User successfully reset their password",
        extra={
            "username": username,
            "user_id": user.id,
            "client_ip_address": client_ip_address,
            "client_user_agent": client_user_agent,
        },
    )

    return None
