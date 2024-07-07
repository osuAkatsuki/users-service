from pydantic import BaseModel

from app.common_types import Mode

import app.state


class UserStats(BaseModel):
    ranked_score: int
    total_score: int
    playcount: int
    replays_watched: int
    total_hits: int
    avg_accuracy: float
    pp: int
    playtime: int
    xh_count: int
    x_count: int
    sh_count: int
    s_count: int
    a_count: int
    b_count: int
    c_count: int
    d_count: int
    max_combo: int


READ_PARAMS = """\
    ranked_score, total_score, playcount, replays_watched, total_hits, avg_accuracy, pp, playtime,
    xh_count, x_count, sh_count, s_count, a_count, b_count, c_count, d_count, max_combo
"""

async def fetch_one_by_user_id_and_mode(
    user_id: int,
    mode: Mode,
) -> UserStats | None:
    query = f"""
        SELECT {READ_PARAMS}
        FROM user_stats
        WHERE user_id = :user_id
        AND mode = :mode
    """
    params = {"user_id": user_id, "mode": mode.value}

    user_stats = await app.state.database.fetch_one(query, params)
    if user_stats is None:
        return None
    
    return UserStats(
        ranked_score=user_stats["ranked_score"],
        total_score=user_stats["total_score"],
        playcount=user_stats["playcount"],
        replays_watched=user_stats["replays_watched"],
        total_hits=user_stats["total_hits"],
        avg_accuracy=user_stats["avg_accuracy"],
        pp=user_stats["pp"],
        playtime=user_stats["playtime"],
        xh_count=user_stats["xh_count"],
        x_count=user_stats["x_count"],
        sh_count=user_stats["sh_count"],
        s_count=user_stats["s_count"],
        a_count=user_stats["a_count"],
        b_count=user_stats["b_count"],
        c_count=user_stats["c_count"],
        d_count=user_stats["d_count"],
        max_combo=user_stats["max_combo"],
    )
