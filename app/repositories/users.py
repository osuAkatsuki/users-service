from datetime import datetime

from pydantic import BaseModel

import app.state
from app.common_types import GameMode
from app.common_types import UserPlayStyle
from app.common_types import UserPrivileges


class User(BaseModel):
    id: int
    username: str
    username_aka: str
    created_at: datetime
    latest_activity: datetime
    userpage_content: str | None
    country: str
    privileges: UserPrivileges
    hashed_password: str
    clan_id: int
    play_style: UserPlayStyle
    favourite_mode: GameMode
    custom_badge_icon: str
    custom_badge_name: str
    can_custom_badge: bool
    show_custom_badge: bool
    silence_reason: str
    silence_end: datetime


READ_PARAMS = """\
    id, username, username_aka, register_datetime, latest_activity, userpage_content, country, privileges, password_md5,
    clan_id, play_style, favourite_mode, custom_badge_icon, custom_badge_name, can_custom_badge, show_custom_badge,
    silence_reason, silence_end
"""


async def fetch_one_by_username(username: str) -> User | None:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM users
        WHERE username_safe = :username_safe
    """
    params = {"username_safe": username.lower().replace(" ", "_")}

    user = await app.state.database.fetch_one(query, params)
    if user is None:
        return None

    return User(
        id=user["id"],
        username=user["username"],
        username_aka=user["username_aka"],
        created_at=datetime.fromtimestamp(user["register_datetime"]),
        latest_activity=datetime.fromtimestamp(user["latest_activity"]),
        userpage_content=user["userpage_content"],
        country=user["country"],
        privileges=UserPrivileges(user["privileges"]),
        hashed_password=user["password_md5"],
        clan_id=user["clan_id"],
        play_style=UserPlayStyle(user["play_style"]),
        favourite_mode=GameMode(user["favourite_mode"]),
        custom_badge_icon=user["custom_badge_icon"],
        custom_badge_name=user["custom_badge_name"],
        can_custom_badge=user["can_custom_badge"],
        show_custom_badge=user["show_custom_badge"],
        silence_reason=user["silence_reason"],
        silence_end=user["silence_end"],
    )


async def fetch_one_by_user_id(user_id: int) -> User | None:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM users
        WHERE id = :user_id
    """
    params = {"user_id": user_id}

    user = await app.state.database.fetch_one(query, params)
    if user is None:
        return None

    return User(
        id=user["id"],
        username=user["username"],
        username_aka=user["username_aka"],
        created_at=datetime.fromtimestamp(user["register_datetime"]),
        latest_activity=datetime.fromtimestamp(user["latest_activity"]),
        userpage_content=user["userpage_content"],
        country=user["country"],
        privileges=UserPrivileges(user["privileges"]),
        hashed_password=user["password_md5"],
        clan_id=user["clan_id"],
        play_style=UserPlayStyle(user["play_style"]),
        favourite_mode=GameMode(user["favourite_mode"]),
        custom_badge_icon=user["custom_badge_icon"],
        custom_badge_name=user["custom_badge_name"],
        can_custom_badge=user["can_custom_badge"],
        show_custom_badge=user["show_custom_badge"],
        silence_reason=user["silence_reason"],
        silence_end=user["silence_end"],
    )


async def username_is_taken(username: str) -> bool:
    query = """\
        SELECT 1
        FROM users
        WHERE username_safe = :username_safe
    """
    username_safe = username.lower().replace(" ", "_")
    params = {"username_safe": username_safe}

    return await app.state.database.fetch_one(query, params) is not None


async def update_username(user_id: int, new_username: str) -> None:
    query = """\
        UPDATE users
        SET username = :new_username,
            username_safe = :new_username_safe
        WHERE id = :user_id
    """
    new_username_safe = new_username.lower().replace(" ", "_")
    params = {
        "new_username": new_username,
        "new_username_safe": new_username_safe,
        "user_id": user_id,
    }

    await app.state.database.execute(query, params)


async def update_password(user_id: int, *, new_hashed_password: str) -> None:
    query = """\
        UPDATE users
        SET password_md5 = :new_hashed_password
        WHERE id = :user_id
    """
    params = {
        "new_hashed_password": new_hashed_password,
        "user_id": user_id,
    }

    await app.state.database.execute(query, params)


async def update_email_address(user_id: int, new_email_address: str) -> None:
    query = """\
        UPDATE users
        SET email = :new_email_address
        WHERE id = :user_id
    """
    params = {
        "new_email_address": new_email_address,
        "user_id": user_id,
    }

    await app.state.database.execute(query, params)


async def fetch_total_registered_user_count() -> int:
    query = """\
        SELECT COUNT(*)
        FROM users
    """
    val = await app.state.database.fetch_val(query)
    if val is None:
        return 0
    return val


async def anonymize_one_by_user_id(user_id: int, /) -> None:
    await app.state.database.execute(
        """\
        UPDATE users
           SET username = :username,
               email = :email,
               userpage_content = :userpage_content,
               country = :country,
               privileges = :privileges,
               clan_id = :clan_id
           WHERE id = :user_id
        """,
        {
            "username": f"deleted_user_{user_id}",
            "email": f"delete_user_{user_id}@example.com",
            "userpage_content": "This user has been deleted.",
            "country": "XX",
            "privileges": UserPrivileges(0),
            "clan_id": 0,
        },
    )


async def fetch_many_by_clan_id(clan_id: int, /) -> list[User]:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM users
        WHERE clan_id = :clan_id
    """
    params = {"clan_id": clan_id}

    users = await app.state.database.fetch_all(query, params)
    return [
        User(
            id=user["id"],
            username=user["username"],
            username_aka=user["username_aka"],
            created_at=datetime.fromtimestamp(user["register_datetime"]),
            latest_activity=datetime.fromtimestamp(user["latest_activity"]),
            userpage_content=user["userpage_content"],
            country=user["country"],
            privileges=UserPrivileges(user["privileges"]),
            hashed_password=user["password_md5"],
            clan_id=user["clan_id"],
            play_style=UserPlayStyle(user["play_style"]),
            favourite_mode=GameMode(user["favourite_mode"]),
            custom_badge_icon=user["custom_badge_icon"],
            custom_badge_name=user["custom_badge_name"],
            can_custom_badge=user["can_custom_badge"],
            show_custom_badge=user["show_custom_badge"],
            silence_reason=user["silence_reason"],
            silence_end=user["silence_end"],
        )
        for user in users
    ]
