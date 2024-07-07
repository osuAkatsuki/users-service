from datetime import datetime
from pydantic import BaseModel

from app.common_types import GameMode
from app.common_types import UserPlayStyle

class TournamentBadge(BaseModel):
    id: int
    name: str
    icon: str

class CustomBadge(BaseModel):
    name: str
    icon: str

class Badge(BaseModel):
    id: int
    name: str
    icon: str
    colour: str

class User(BaseModel):
    id: int
    username: str
    username_aka: str
    created_at: datetime
    latest_activity: datetime
    userpage_content: str
    country: str
    clan_id: int
    followers: int
    favourite_mode: GameMode
    play_style: UserPlayStyle
    badges: list[Badge]
    tournament_badges: list[TournamentBadge]
    can_custom_badge: bool
    show_custom_badge: bool
    custom_badge: CustomBadge
    silence_end: datetime
    silence_reason: str
