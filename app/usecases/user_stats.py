from app.common_types import AkatsukiMode
from app.models.user_stats import UserStats
from app.errors import Error
from app.errors import ErrorCode
from app.repositories import user_stats


async def fetch_one_by_user_id_and_akatsuki_mode(
    user_id: int, mode: AkatsukiMode
) -> UserStats | Error:
    stats = await user_stats.fetch_one_by_user_id_and_akatsuki_mode(user_id, mode)
    if stats is None:
        return Error(
            error_code=ErrorCode.NOT_FOUND,
            user_feedback="User statistics not found.",
        )

    return UserStats(
        ranked_score=stats.ranked_score,
        total_score=stats.total_score,
        play_count=stats.playcount,
        replays_watched=stats.replays_watched,
        total_hits=stats.total_hits,
        accuracy=stats.avg_accuracy,
        pp=stats.pp,
        play_time=stats.playtime,
        ssh_count=stats.xh_count,
        ss_count=stats.x_count,
        sh_count=stats.sh_count,
        s_count=stats.s_count,
        a_count=stats.a_count,
        b_count=stats.b_count,
        c_count=stats.c_count,
        d_count=stats.d_count,
        max_combo=stats.max_combo,
    )


async def fetch_global_all_time_pp_earned() -> int:
    return await user_stats.fetch_global_all_time_pp_earned()
