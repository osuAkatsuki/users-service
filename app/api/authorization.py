from app import security
from app.common_types import UserPrivileges
from app.errors import Error
from app.errors import ErrorCode
from app.repositories import access_tokens
from app.repositories import users


async def authorize_request(
    *,
    user_access_token: str,
    expected_user_id: int | None = None,
) -> access_tokens.AccessToken | Error:
    hashed_access_token = security.hash_secure_token(user_access_token)
    trusted_access_token = await access_tokens.fetch_one(hashed_access_token)
    if trusted_access_token is None:
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Unauthorized request",
        )

    if (
        expected_user_id is not None
        and trusted_access_token.user_id != expected_user_id
    ):
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Unauthorized request",
        )

    user = await users.fetch_one_by_user_id(trusted_access_token.user_id)
    if (
        user is None
        or not user.privileges & UserPrivileges.USER_NORMAL
        or user.privileges & UserPrivileges.USER_PENDING_VERIFICATION
    ):
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Unauthorized request",
        )

    return trusted_access_token
