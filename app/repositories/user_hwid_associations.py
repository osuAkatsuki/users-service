from typing import Any

from pydantic import BaseModel

import app.state


class UserHwidAssociation(BaseModel):
    id: int
    userid: int
    mac: str
    unique_id: str
    disk_id: str
    occurencies: int
    activated: bool


READ_PARAMS = """\
    id, userid, mac, unique_id, disk_id, occurencies, activated
"""


async def delete_many_by_user_id(user_id: int, /) -> list[UserHwidAssociation]:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM hw_user
        WHERE userid = :user_id
    """
    params: dict[str, Any] = {"user_id": user_id}
    recs = await app.state.database.fetch_all(query, params)
    if not recs:
        return []

    query = """\
        DELETE FROM hw_user
        WHERE userid = :user_id
    """
    params = {"user_id": user_id}
    await app.state.database.execute(query, params)

    return [
        UserHwidAssociation(
            id=rec["id"],
            userid=rec["userid"],
            mac=rec["mac"],
            unique_id=rec["unique_id"],
            disk_id=rec["disk_id"],
            occurencies=rec["occurencies"],
            activated=rec["activated"],
        )
        for rec in recs
    ]
