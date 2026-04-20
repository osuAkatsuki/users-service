from datetime import datetime
from datetime import time
from typing import Any

from pydantic import BaseModel

import app.state


class ScoreSubmissionLog(BaseModel):
    id: str
    score_id: int
    uninstall_id_hash: str
    disk_signature_hash: str
    client_version: str
    client_hash: str
    score_time_elapsed: time
    osu_auth_token: str | None
    created_at: datetime


READ_PARAMS = """\
    id, score_id, uninstall_id_hash, disk_signature_hash, client_version,
    client_hash, score_time_elapsed, osu_auth_token, created_at
"""


async def delete_many_by_user_id_via_scores_tables(
    user_id: int,
    /,
) -> list[ScoreSubmissionLog]:
    query = f"""\
        WITH score_ids AS (
            SELECT id FROM scores WHERE user_id = :user_id
            UNION
            SELECT id FROM scores_relax WHERE user_id = :user_id
            UNION
            SELECT id FROM scores_ap WHERE user_id = :user_id
        )
        SELECT {READ_PARAMS}
        FROM score_submission_logs
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
        DELETE FROM score_submission_logs
        WHERE score_id IN score_ids
    """
    params = {"user_id": user_id}
    await app.state.database.execute(query, params)

    return [
        ScoreSubmissionLog(
            id=rec["id"],
            score_id=rec["score_id"],
            uninstall_id_hash=rec["uninstall_id_hash"],
            disk_signature_hash=rec["disk_signature_hash"],
            client_version=rec["client_version"],
            client_hash=rec["client_hash"],
            score_time_elapsed=rec["score_time_elapsed"],
            osu_auth_token=rec["osu_auth_token"],
            created_at=rec["created_at"],
        )
        for rec in recs
    ]
