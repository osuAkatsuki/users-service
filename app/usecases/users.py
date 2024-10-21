from app import security
from app.common_types import UserPrivileges
from app.errors import Error
from app.errors import ErrorCode
from app.models.users import Badge
from app.models.users import CustomBadge
from app.models.users import TournamentBadge
from app.models.users import User
from app.repositories import clans
from app.repositories import password_recovery
from app.repositories import user_badges
from app.repositories import user_hwid_associations
from app.repositories import user_ip_associations
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

    if not security.check_osu_password(
        untrusted_password=current_password,
        hashed_password=user.hashed_password,
    ):
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Incorrect password.",
        )

    hashed_password = security.hash_osu_password(new_password)
    await users.update_password(user_id, new_hashed_password=hashed_password)
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

    if not security.check_osu_password(
        untrusted_password=current_password,
        hashed_password=user.hashed_password,
    ):
        return Error(
            error_code=ErrorCode.INCORRECT_CREDENTIALS,
            user_feedback="Incorrect password.",
        )

    await users.update_email_address(user_id, new_email_address)
    return None


async def fetch_total_registered_user_count() -> int:
    return await users.fetch_total_registered_user_count()


async def delete_one_by_user_id(user_id: int, /) -> None | Error:

    # sql tables associated with users:
    # - [anonymize] users
    # - [leave as-is] users_stats
    # - [leave as-is] rx_stats
    # - [leave as-is] ap_stats
    # - [TODO/AC] ip_user
    # - [TODO/AC] hw_user
    # - [leave as-is] user_badges
    # - [leave as-is] user_tourmnt_badges
    # - [leave as-is] user_achievements
    # - [transfer perms if owner & kick] clans
    # - [leave as-is] identity_tokens
    # - [leave as-is] irc_tokens
    # - [TODO/AC] lastfm_flags
    # - [leave as-is] beatmaps_rating
    # - [leave as-is] clan_requests (empty?)
    # - [leave as-is] comments
    # - [leave as-is] matches
    # - [leave as-is] match_eventrs
    # - [leave as-is] match_games
    # - [leave as-is] match_game_scores
    # - [TODO/financial] notifications
    # - [delete; key'd by username??] password_recovery
    # - [TODO/AC] patcher_detections
    # - [TODO/AC] patcher_token_logs
    # - [TODO] profile_backgrounds (and filesystem data)
    # - [TODO] rap_logs
    # - [leave as-is] remember
    # - [leave as-is] reports
    # - [leave as-is] rework_queue
    # - [leave as-is] rework_scores
    # - [leave as-is] rework_stats
    # - [leave as-is] scheduled_bans
    # - [leave as-is] scores
    # - [leave as-is] scores_ap
    # - [leave as-is] scores_relax
    # - [leave as-is] scores_first
    # - [TODO/AC] score_submission_logs
    # - [leave as-is] tokens
    # - [leave as-is] user_relationships
    # - [leave as-is] user_beatmaps
    # - [leave as-is] user_favourites
    # - [leave as-is] user_profile_history
    # - [leave as-is] user_speedruns
    # - [leave as-is] user_tokens

    # misc.
    # - [anonymize] replay data for all scores
    # - [TODO] youtube uploads

    # PII to focus on:
    # - username / username aka
    # - email
    # - clan association
    # - country
    # - (potetnailly) user notes
    # - (potentially) userpage content

    user = await users.fetch_one_by_user_id(user_id)
    if user is None:
        return Error(
            error_code=ErrorCode.NOT_FOUND,
            user_feedback="User not found.",
        )

    if user.clan_id:
        clan = await clans.fetch_one_by_clan_id(user.clan_id)
        if clan is not None:
            if user.id == clan.owner:
                # transfer clan ownership to another member, if available
                other_clan_members = sorted(
                    [
                        u
                        for u in await users.fetch_many_by_clan_id(user.clan_id)
                        if u.id != user.id
                    ],
                    # XXX: heuristic; clan join date would be better
                    #      but it is not something we currently store
                    key=lambda u: (u.privileges, u.latest_activity),
                )
                if other_clan_members:
                    new_owner = other_clan_members[0]
                    await clans.update_owner(user.clan_id, new_owner.id)
                else:
                    # no other members in the clan; just delete it
                    await clans.delete_one_by_clan_id(user.clan_id)

    await password_recovery.delete_many_by_username(user.username)

    # TODO: consider what ac data should be anonymized instead of wiped
    await user_ip_associations.delete_many_by_user_id(user_id)
    await user_hwid_associations.delete_many_by_user_id(user_id)

    # TODO: wipe all replay data
    # TODO: wipe all associated content
    # TODO: potentially wipe youtube uploads

    # last step of the process; remove all associated pii
    await users.anonymize_one_by_user_id(user_id)

    return None
