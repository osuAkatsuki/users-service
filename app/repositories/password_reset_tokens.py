from datetime import datetime

from pydantic import BaseModel

import app.state

# A reset token is valid for strictly less than this many seconds after
# creation; at or beyond it the token is expired. Judged on the DB clock.
PASSWORD_RESET_TOKEN_TTL_SECONDS = 3600


class PasswordResetToken(BaseModel):
    id: int
    hashed_token: str
    username: str
    created_at: datetime


READ_PARAMS = """\
    id, k, u, t
"""


async def create(*, username: str, hashed_token: str) -> PasswordResetToken:
    # `t` is set with the same DB clock that expiry is compared against in
    # fetch_one, rather than relying on the column's schema-level default.
    query = """\
        INSERT INTO password_recovery (k, u, t)
        VALUES (:hashed_token, :username, NOW())
    """
    params = {"hashed_token": hashed_token, "username": username}
    await app.state.database.execute(query, params)

    query = f"""\
        SELECT {READ_PARAMS}
        FROM password_recovery
        WHERE k = :hashed_token
    """
    params = {"hashed_token": hashed_token}
    rec = await app.state.database.fetch_one(query, params)
    assert rec is not None
    return PasswordResetToken(
        id=rec["id"],
        hashed_token=rec["k"],
        username=rec["u"],
        created_at=rec["t"],
    )


async def fetch_one(hashed_token: str) -> PasswordResetToken | None:
    # Expiry is evaluated on the DB clock (NOW()), matching the NOW() written by
    # create(), so it is immune to app/DB timezone or clock skew. The predicate
    # is framed as "is valid" so a NULL age fails closed to expired: a NOT NULL
    # `t` should never yield NULL, but a corrupted/migrated row must not be
    # silently accepted.
    query = """\
        SELECT id, u, t,
               TIMESTAMPDIFF(SECOND, t, NOW()) < :ttl_seconds AS is_valid
        FROM password_recovery
        WHERE k = :hashed_token
    """
    params = {
        "hashed_token": hashed_token,
        "ttl_seconds": PASSWORD_RESET_TOKEN_TTL_SECONDS,
    }
    rec = await app.state.database.fetch_one(query, params)
    if rec is None:
        return None

    if not rec["is_valid"]:
        # Expired (or otherwise non-valid): delete the dead row and report it as
        # absent, so callers cannot tell "expired" apart from "never existed".
        await delete_one(hashed_token)
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
