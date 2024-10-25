from typing import Any

from pydantic import BaseModel

import app.state


class UserIpAssociation(BaseModel):
    id: int
    userid: int
    ip: str
    occurencies: int


READ_PARAMS = """\
    id, userid, ip, occurencies
"""


async def delete_many_by_user_id(user_id: int, /) -> list[UserIpAssociation]:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM ip_user
        WHERE userid = :user_id
    """
    params: dict[str, Any] = {"user_id": user_id}
    recs = await app.state.database.fetch_all(query, params)
    if not recs:
        return []

    query = """\
        DELETE FROM ip_user
        WHERE userid = :user_id
    """
    params = {"user_id": user_id}
    await app.state.database.execute(query, params)

    return [
        UserIpAssociation(
            id=rec["id"],
            userid=rec["userid"],
            ip=rec["ip"],
            occurencies=rec["occurencies"],
        )
        for rec in recs
    ]
