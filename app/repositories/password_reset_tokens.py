from pydantic import BaseModel

import app.state


class PasswordResetToken(BaseModel):
    id: int
    hashed_token: str
    username: str
    created_at: int


READ_PARAMS = """\
    id, k, u, t
"""


async def create(*, username: str, hashed_token: str) -> PasswordResetToken:
    query = """\
        INSERT INTO password_recovery (k, u, t)
        VALUES (:hashed_token, :username, UNIX_TIMESTAMP())
    """
    params = {"hashed_token": hashed_token, "username": username}
    await app.state.database.execute(query, params)

    query = f"""\
        SELECT {READ_PARAMS}
        FROM password_recovery
        WHERE k = :hashed_token
    """
    rec = await app.state.database.fetch_one(query, params)
    assert rec is not None
    return PasswordResetToken(
        id=rec["id"],
        hashed_token=rec["k"],
        username=rec["u"],
        created_at=rec["t"],
    )


async def fetch_one(hashed_token: str) -> PasswordResetToken | None:
    query = """\
        SELECT id, u, t
        FROM password_recovery
        WHERE k = :hashed_token
    """
    params = {"hashed_token": hashed_token}
    rec = await app.state.database.fetch_one(query, params)
    if rec is None:
        return None

    return PasswordResetToken(
        id=rec["id"],
        hashed_token=hashed_token,
        username=rec["u"],
        created_at=rec["t"],
    )


async def delete_one(hashed_token: str) -> None:
    query = """\
        DELETE FROM password_recovery
        WHERE k = :hashed_token
    """
    params = {"hashed_token": hashed_token}
    await app.state.database.execute(query, params)
