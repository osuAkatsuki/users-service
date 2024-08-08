from app import security
from app.common_types import UserPrivileges
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


async def update_username(user_id: int, *, new_username: str) -> None | Error:
    user = await users.fetch_one_by_user_id(user_id)
    if user is None:
        return Error(
            error_code=ErrorCode.NOT_FOUND,
            user_feedback="User not found.",
        )

    # TODO: implement the one-free-name-change policy

    if not user.privileges & UserPrivileges.USER_DONOR:
        return Error(
            error_code=ErrorCode.INSUFFICIENT_PRIVILEGES,
            user_feedback="Only donor may change their usernames.",
        )

    exists = await users.username_is_taken(new_username)
    if exists:
        return Error(
            error_code=ErrorCode.CONFLICT,
            user_feedback="Username is already taken.",
        )

    await users.update_username(user_id, new_username)
    return None


async def update_password(
    user_id: int,
    *,
    current_password: str,
    new_password: str,
) -> None | Error:
    user = await users.fetch_one_by_user_id(user_id)
    if user is None:
        return Error(
            error_code=ErrorCode.NOT_FOUND,
            user_feedback="User not found.",
        )

    if security.check_osu_password(user.hashed_password, current_password):
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Incorrect password.",
        )

    await users.update_password(user_id, new_password)
    return None


async def update_email_address(
    user_id: int,
    *,
    current_password: str,
    new_email_address: str,
) -> None | Error:
    user = await users.fetch_one_by_user_id(user_id)
    if user is None:
        return Error(
            error_code=ErrorCode.NOT_FOUND,
            user_feedback="User not found.",
        )

    if security.check_osu_password(user.hashed_password, current_password):
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Incorrect password.",
        )

    await users.update_email_address(user_id, new_email_address)
    return None
