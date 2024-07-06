from pydantic import BaseModel
from app.common_types import UserPrivileges
import app.state

import hashlib


class AccessToken(BaseModel):
    access_token: str
    user_id: int
    privileges: UserPrivileges
    description: str
    private: bool


READ_PARAMS = """\
    user, privileges, description, token, private
"""


async def create(*, user_id: int, access_token: str) -> AccessToken:
    query = """\
        INSERT INTO tokens (user, privileges, description, token, private)
        VALUES (:user_id, 0, 'Access token', :access_token, TRUE)
    """
    hashed_access_token = hashlib.md5(access_token.encode()).hexdigest()
    params = {"user_id": user_id, "access_token": hashed_access_token}
    await app.state.database.execute(query, params)
    query = f"""\
        SELECT {READ_PARAMS}
        FROM tokens
        WHERE token = :access_token
    """
    params = {"access_token": hashed_access_token}
    rec = await app.state.database.fetch_one(query, params)
    assert rec is not None
    return AccessToken(
        access_token=access_token,
        user_id=rec["user"],
        privileges=UserPrivileges(rec["privileges"]),
        description=rec["description"],
        private=rec["private"],
    )
