from app.errors import Error
from app.errors import ErrorCode
from app.models.users import Badge
from app.models.users import CustomBadge
from app.models.users import TournamentBadge
from app.models.users import User
from app.repositories import user_badges
from app.repositories import user_relationships
from app.repositories import user_tournament_badges
from app.repositories import users


async def fetch_one_by_username(username: str) -> User | Error:
    user = await users.fetch_one_by_username(username)
    if user is None:
        return Error(error_code=ErrorCode.NOT_FOUND, user_feedback="User not found.")

    followers = await user_relationships.fetch_follower_count_by_user_id(user.id)
    badges = await user_badges.fetch_all_by_user_id(user.id)
    tournament_badges = await user_tournament_badges.fetch_all_by_user_id(user.id)

    return User(
        id=user.id,
        username=user.username,
        username_aka=user.username_aka,
        created_at=user.created_at,
        latest_activity=user.latest_activity,
        userpage_content=user.userpage_content,
        country=user.country,
        clan_id=user.clan_id,
        followers=followers,
        favourite_mode=user.favourite_mode,
        play_style=user.play_style,
        badges=[
            Badge(
                id=badge.id,
                name=badge.name,
                icon=badge.icon,
                colour=badge.colour,
            )
            for badge in badges
        ],
        tournament_badges=[
            TournamentBadge(
                id=tournament_badge.id,
                name=tournament_badge.name,
                icon=tournament_badge.icon,
            )
            for tournament_badge in tournament_badges
        ],
        can_custom_badge=user.can_custom_badge,
        show_custom_badge=user.show_custom_badge,
        custom_badge=CustomBadge(
            name=user.custom_badge_name,
            icon=user.custom_badge_icon,
        ),
        silence_end=user.silence_end,
        silence_reason=user.silence_reason,
    )


async def fetch_one_by_user_id(user_id: int) -> User | Error:
    user = await users.fetch_one_by_user_id(user_id)
    if user is None:
        return Error(error_code=ErrorCode.NOT_FOUND, user_feedback="User not found.")

    followers = await user_relationships.fetch_follower_count_by_user_id(user.id)
    badges = await user_badges.fetch_all_by_user_id(user.id)
    tournament_badges = await user_tournament_badges.fetch_all_by_user_id(user.id)

    return User(
        id=user.id,
        username=user.username,
        username_aka=user.username_aka,
        created_at=user.created_at,
        latest_activity=user.latest_activity,
        userpage_content=user.userpage_content,
        country=user.country,
        clan_id=user.clan_id,
        followers=followers,
        favourite_mode=user.favourite_mode,
        play_style=user.play_style,
        badges=[
            Badge(
                id=badge.id,
                name=badge.name,
                icon=badge.icon,
                colour=badge.colour,
            )
            for badge in badges
        ],
        tournament_badges=[
            TournamentBadge(
                id=tournament_badge.id,
                name=tournament_badge.name,
                icon=tournament_badge.icon,
            )
            for tournament_badge in tournament_badges
        ],
        can_custom_badge=user.can_custom_badge,
        show_custom_badge=user.show_custom_badge,
        custom_badge=CustomBadge(
            name=user.custom_badge_name,
            icon=user.custom_badge_icon,
        ),
        silence_end=user.silence_end,
        silence_reason=user.silence_reason,
    )
