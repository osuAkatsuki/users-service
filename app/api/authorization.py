from app import security
from app.errors import Error
from app.errors import ErrorCode
from app.repositories import tokens
from app.repositories.tokens import TokenType


async def authorize_request(
    *,
    user_access_token: str,
    expected_user_id: int | None = None,
) -> tokens.Token | Error:
    hashed_access_token = security.hash_access_token(user_access_token)
    trusted_access_token = await tokens.fetch_one(
        hashed_access_token,
        token_type=TokenType.ACCESS_TOKEN,
    )
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

    return trusted_access_token
