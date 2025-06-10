from pydantic import BaseModel

import app.state
from app.common_types import UserPrivileges


class AccessToken(BaseModel):
    hashed_access_token: str
    user_id: int
    privileges: UserPrivileges
    description: str
    private: bool
    last_updated: int


READ_PARAMS = """\
    user, privileges, description, token, private, last_updated
"""


async def create(*, user_id: int, hashed_access_token: str) -> AccessToken:
    query = """\
        INSERT INTO tokens (user, privileges, description, token, private, last_updated)
        VALUES (:user_id, 0, 'Access token', :hashed_access_token, TRUE, UNIX_TIMESTAMP())
    """
    params = {"user_id": user_id, "hashed_access_token": hashed_access_token}
    await app.state.database.execute(query, params)
    query = f"""\
        SELECT {READ_PARAMS}
        FROM tokens
        WHERE token = :hashed_access_token
    """
    params = {"hashed_access_token": hashed_access_token}
    rec = await app.state.database.fetch_one(query, params)
    assert rec is not None
    return AccessToken(
        hashed_access_token=hashed_access_token,
        user_id=rec["user"],
        privileges=UserPrivileges(rec["privileges"]),
        description=rec["description"],
        private=rec["private"],
        last_updated=rec["last_updated"],
    )


async def fetch_one(hashed_access_token: str) -> AccessToken | None:
    query = """\
        SELECT user, privileges, description, private, last_updated
        FROM tokens
        WHERE token = :hashed_access_token
    """
    params = {"hashed_access_token": hashed_access_token}
    rec = await app.state.database.fetch_one(query, params)
    if rec is None:
        return None

    return AccessToken(
        hashed_access_token=hashed_access_token,
        user_id=rec["user"],
        privileges=UserPrivileges(rec["privileges"]),
        description=rec["description"],
        private=rec["private"],
        last_updated=rec["last_updated"],
    )


async def delete_one(hashed_access_token: str) -> None:
    query = """\
        DELETE FROM tokens
        WHERE token = :hashed_access_token
    """
    params = {"hashed_access_token": hashed_access_token}
    await app.state.database.execute(query, params)
