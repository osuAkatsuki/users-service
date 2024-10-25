from enum import IntEnum

from pydantic import BaseModel

import app.state


class ClanStatus(IntEnum):
    CLOSED = 0
    OPEN_FOR_ALL = 1
    INVITE_ONLY = 2
    REQUEST_TO_JOIN = 3


class Clan(BaseModel):
    id: int
    name: str
    tag: str
    description: str
    icon: str
    background: str
    owner: int
    invite: str
    status: ClanStatus


READ_PARAMS = """\
    id, name, tag, description, icon, background, owner, invite, status
"""


async def fetch_one_by_clan_id(clan_id: int, /) -> Clan | None:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM clans
        WHERE id = :clan_id
    """
    params = {"clan_id": clan_id}

    clan = await app.state.database.fetch_one(query, params)
    if clan is None:
        return None

    return Clan(
        id=clan["id"],
        name=clan["name"],
        tag=clan["tag"],
        description=clan["description"],
        icon=clan["icon"],
        background=clan["background"],
        owner=clan["owner"],
        invite=clan["invite"],
        status=ClanStatus(clan["status"]),
    )


async def update_owner(clan_id: int, new_owner: int) -> None:
    query = """\
        UPDATE clans
        SET owner = :new_owner
        WHERE id = :clan_id
    """
    params = {"new_owner": new_owner, "clan_id": clan_id}

    await app.state.database.execute(query, params)


async def delete_one_by_clan_id(clan_id: int, /) -> None:
    query = """\
        DELETE FROM clans
        WHERE id = :clan_id
    """
    params = {"clan_id": clan_id}

    await app.state.database.execute(query, params)
