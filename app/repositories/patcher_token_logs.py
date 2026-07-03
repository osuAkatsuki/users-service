from datetime import datetime
from typing import Any

from pydantic import BaseModel

import app.state


class PatcherTokenLog(BaseModel):
    id: str
    score_id: int
    client_hash: str
    commentary: str | None
    token_generated_at: datetime
    created_at: datetime
    updated_at: datetime


READ_PARAMS = """\
    id, score_id, client_hash, commentary, token_generated_at, created_at, updated_at
"""


async def delete_many_by_user_id_via_scores_tables(
    user_id: int,
    /,
) -> list[PatcherTokenLog]:
    query = f"""\
        WITH score_ids AS (
            SELECT id FROM scores WHERE user_id = :user_id
            UNION
            SELECT id FROM scores_relax WHERE user_id = :user_id
            UNION
            SELECT id FROM scores_ap WHERE user_id = :user_id
        )
        SELECT {READ_PARAMS}
        FROM patcher_token_logs
        WHERE score_id IN score_ids
    """
    params: dict[str, Any] = {"user_id": user_id}
    recs = await app.state.database.fetch_all(query, params)
    if not recs:
        return []

    query = """\
        WITH score_ids AS (
            SELECT id FROM scores WHERE user_id = :user_id
            UNION
            SELECT id FROM scores_relax WHERE user_id = :user_id
            UNION
            SELECT id FROM scores_ap WHERE user_id = :user_id
        )
        DELETE FROM patcher_token_logs
        WHERE score_id IN score_ids
    """
    params = {"user_id": user_id}
    await app.state.database.execute(query, params)

    return [
        PatcherTokenLog(
            id=rec["id"],
            score_id=rec["score_id"],
            client_hash=rec["client_hash"],
            commentary=rec["commentary"],
            token_generated_at=rec["token_generated_at"],
            created_at=rec["created_at"],
            updated_at=rec["updated_at"],
        )
        for rec in recs
    ]
