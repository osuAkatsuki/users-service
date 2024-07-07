from pydantic import BaseModel

import app.state


class Badge(BaseModel):
    id: int
    name: str
    icon: str
    colour: str


READ_PARAMS = """\
    badges.id, badges.name, badges.icon, badges.colour
"""


async def fetch_all_by_user_id(user_id: int) -> list[Badge]:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM user_badges
        INNER JOIN badges
        ON user_badges.badge = badges.id
        WHERE user_badges.user = :user_id
    """
    params = {"user_id": user_id}

    badges = await app.state.database.fetch_all(query, params)

    return [
        Badge(
            id=badge["id"],
            name=badge["name"],
            icon=badge["icon"],
            colour=badge["colour"],
        )
        for badge in badges
    ]
