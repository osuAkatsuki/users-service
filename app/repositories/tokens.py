from enum import StrEnum

from pydantic import BaseModel

import app.state
from app.common_types import UserPrivileges


class TokenType(StrEnum):
    ACCESS_TOKEN = "Access Token"
    PASSWORD_RESET_TOKEN = "Password Reset Token"


class Token(BaseModel):
    hashed_token: str
    user_id: int
    privileges: UserPrivileges
    token_type: TokenType
    private: bool
    last_updated: int


READ_PARAMS = """\
    user, privileges, description, token, private, last_updated
"""


async def create(
    *,
    user_id: int,
    hashed_token: str,
    token_type: TokenType,
) -> Token:
    query = """\
        INSERT INTO tokens (user, privileges, description, token, private, last_updated)
        VALUES (:user_id, 0, :description, :hashed_token, TRUE, UNIX_TIMESTAMP())
    """
    params = {
        "user_id": user_id,
        "description": token_type.value,
        "hashed_token": hashed_token,
    }
    await app.state.database.execute(query, params)
    query = f"""\
        SELECT {READ_PARAMS}
        FROM tokens
        WHERE token = :hashed_token
    """
    params = {"hashed_token": hashed_token}
    rec = await app.state.database.fetch_one(query, params)
    assert rec is not None
    return Token(
        hashed_token=hashed_token,
        user_id=rec["user"],
        privileges=UserPrivileges(rec["privileges"]),
        token_type=TokenType(rec["description"]),
        private=rec["private"],
        last_updated=rec["last_updated"],
    )


async def fetch_one(
    hashed_token: str,
    token_type: TokenType,
) -> Token | None:
    query = """\
        SELECT user, privileges, description, private, last_updated
        FROM tokens
        WHERE token = :hashed_token
        AND description = :description
    """
    params = {
        "hashed_token": hashed_token,
        "description": token_type.value,
    }
    rec = await app.state.database.fetch_one(query, params)
    if rec is None:
        return None

    return Token(
        hashed_token=hashed_token,
        user_id=rec["user"],
        privileges=UserPrivileges(rec["privileges"]),
        token_type=TokenType(rec["description"]),
        private=rec["private"],
        last_updated=rec["last_updated"],
    )


async def delete_one(hashed_token: str, token_type: TokenType) -> None:
    query = """\
        DELETE FROM tokens
        WHERE token = :hashed_token
        AND description = :description
    """
    params = {
        "hashed_token": hashed_token,
        "description": token_type.value,
    }
    await app.state.database.execute(query, params)
