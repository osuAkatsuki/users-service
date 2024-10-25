from datetime import datetime
from enum import IntEnum

from pydantic import BaseModel

import app.state


class PasswordRecovery(BaseModel):
    id: int
    k: str  # key
    u: str  # username
    t: datetime


READ_PARAMS = """\
    id, k, u, t
"""


async def delete_many_by_username(username: str, /) -> list[PasswordRecovery]:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM password_recovery
        WHERE u = :username
    """
    params = {"username": username}
    recs = await app.state.database.fetch_all(query, params)
    if not recs:
        return []

    query = """\
        DELETE FROM password_recovery
        WHERE u = :username
    """
    params = {"username": username}
    await app.state.database.execute(query, params)

    return [
        PasswordRecovery(
            id=rec["id"],
            k=rec["k"],
            u=rec["u"],
            t=rec["t"],
        )
        for rec in recs
    ]
