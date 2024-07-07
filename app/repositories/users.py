from pydantic import BaseModel
from datetime import datetime

import app.state
from app.common_types import UserPrivileges
from app.common_types import UserPlayStyle
from app.common_types import GameMode


class User(BaseModel):
    id: int
    username: str
    username_aka: str
    created_at: datetime
    latest_activity: datetime
    userpage_content: str
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
