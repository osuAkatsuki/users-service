from pydantic import BaseModel

import app.state

class TournamentBadge(BaseModel):
    id: int
    name: str
    icon: str

READ_PARAMS = """\
    tourmnt_badges.id, tourmnt_badges.name, tourmnt_badges.icon
"""

async def fetch_all_by_user_id(user_id: int) -> list[TournamentBadge]:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM user_tourmnt_badges
        INNER JOIN tourmnt_badges
        ON user_tourmnt_badges.badge = tourmnt_badges.id
        WHERE user_tourmnt_badges.user = :user_id
    """
    params = {"user_id": user_id}

    tournament_badges = await app.state.database.fetch_all(query, params)

    return [
        TournamentBadge(
            id=tournament_badge["id"],
            name=tournament_badge["name"],
            icon=tournament_badge["icon"],
        )
        for tournament_badge in tournament_badges
    ]
