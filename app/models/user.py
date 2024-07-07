from pydantic import BaseModel
from datetime import datetime

from app.models.tournament_badge import TournamentBadge
from app.models.custom_badge import CustomBadge
from app.common_types import UserPlayStyle
from app.common_types import GameMode
from app.models.badge import Badge

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
    custom_badge: CustomBadge
    silence_end: datetime
    silence_reason: str
