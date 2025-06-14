import logging
import time

import app.state
from app import security
from app.adapters import amplitude
from app.adapters import assets
from app.adapters import recaptcha
from app.common_types import AkatsukiMode
from app.common_types import UserPrivileges
from app.errors import Error
from app.errors import ErrorCode
from app.models.authentication import AuthorizationGrant
from app.models.authentication import Identity
from app.models.users import Badge
from app.models.users import CustomBadge
from app.models.users import TournamentBadge
from app.models.users import User
from app.repositories import access_tokens
from app.repositories import clans
from app.repositories import lastfm_flags
from app.repositories import password_recovery
from app.repositories import user_badges
from app.repositories import user_hwid_associations
from app.repositories import user_ip_associations
from app.repositories import user_relationships
from app.repositories import user_stats
from app.repositories import user_tournament_badges
from app.repositories import users


async def create_and_authenticate_user(
    *,
    username: str,
    email_address: str,
    password: str,
    recaptcha_token: str,
    client_ip_address: str,
    client_user_agent: str,
) -> AuthorizationGrant | Error:
    # "SELECT value_int FROM system_settings WHERE name = 'registrations_enabled'").Scan(&enabled)

    if not security.validate_username(username):
        return Error(
            error_code=ErrorCode.BAD_REQUEST,
            user_feedback="Username does not meet requirements.",
        )

    if not security.validate_email_address(email_address):
        return Error(
            error_code=ErrorCode.BAD_REQUEST,
            user_feedback="Email address does not meet requirements.",
        )

    if not security.validate_password(password):
        return Error(
            error_code=ErrorCode.BAD_REQUEST,
            user_feedback="Password does not meet requirements.",
        )

    if await users.username_is_taken(username):
        return Error(
            error_code=ErrorCode.CONFLICT,
            user_feedback="Username is already taken.",
        )

    if await users.email_address_is_taken(email_address):
        return Error(
            error_code=ErrorCode.CONFLICT,
            user_feedback="Email address is already taken.",
        )

    if not await recaptcha.verify_recaptcha(
        recaptcha_token=recaptcha_token,
        client_ip_address=client_ip_address,
    ):
        return Error(
            error_code=ErrorCode.BAD_REQUEST,
            user_feedback="Invalid reCAPTCHA response.",
        )

    hashed_password = security.hash_osu_password(password)

    # TODO: database transaction for atomicity
    user = await users.create(
        username=username,
        email_address=email_address,
        hashed_password=hashed_password,
    )
    for akatsuki_mode in AkatsukiMode:
        await user_stats.create(
            user_id=user.id,
            akatsuki_mode=akatsuki_mode,
        )

    await amplitude.track(
        user_id=str(user.id),
        event_name="web_signup",
        ip=client_ip_address,
        # TODO: country, city, region from CF ips
        # TODO: language from accept-language header
        # TODO: os name, version, device model from user agent
        event_properties={"source": "users-service"},
        user_properties={
            "username": user.username,
            "email": user.email,  # TODO: remove
            "signup_date": int(time.time()),
            "signup_ip": client_ip_address,
        },
    )

    # TODO: what is the "Y" cookie?

    await app.state.redis.incr("ripple:registered_users")

    unhashed_access_token = security.generate_unhashed_secure_token()
    hashed_access_token = security.hash_secure_token(unhashed_access_token)
    access_token = await access_tokens.create(
        user_id=user.id,
        hashed_access_token=hashed_access_token,
    )

    # TODO: insert into ip_user table?

    logging.info(
        "User successfully signed up",
        extra={
            "user_id": user.id,
            "client_ip_address": client_ip_address,
            "client_user_agent": client_user_agent,
        },
    )

    # TODO: make sure they're sent to a verification flow on the FE

    return AuthorizationGrant(
        # XXX: intentionally send back the unhashed access token
        unhashed_access_token=unhashed_access_token,
        privileges=access_token.privileges,
        expires_at=None,
        identity=Identity(
            user_id=user.id,
            username=user.username,
            privileges=user.privileges,
        ),
    )


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

    if not security.validate_username(new_username):
        return Error(
            error_code=ErrorCode.BAD_REQUEST,
            user_feedback="Username does not meet requirements.",
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

    if not security.validate_password(new_password):
        return Error(
            error_code=ErrorCode.BAD_REQUEST,
            user_feedback="Password does not meet security requirements.",
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
    """\
    An anonymization process for user deletion, mainly implemented
    for the purpose of complying with GDPR, CCPA and other regulations.
    """
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
    # - [leave as-is] match_events
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

    transaction = await app.state.database.transaction()
    try:
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
        await lastfm_flags.delete_many_by_user_id(user_id)
        # TODO: patcher_detections & patcher_token_logs

        # TODO: wipe or anonymize all replay data.
        #       probably a good idea to call scores-service

        # TODO: wipe all static content (screenshots, profile bgs, etc.)
        # TODO: potentially wipe youtube uploads

        # last step of the process; remove all associated pii
        # TODO: split this to make it more clear what's being done
        #       at the usecase layer
        await users.anonymize_one_by_user_id(user_id)
        await assets.delete_avatar_by_user_id(user_id)

        # TODO: (technically required) anonymize data in data backups

        # inform other systems of the user's deletion (or "ban")
        await app.state.redis.publish("peppy:ban", str(user_id))

        # TODO: make sure they're removed from leaderboards
    except Exception:
        logging.exception(
            "Failed to process GDPR/CCPA user deletion request",
            extra={"user_id": user_id},
        )
        await transaction.rollback()
        return Error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            user_feedback="Failed to process user deletion request.",
        )
    else:
        logging.info(
            "Successfully processed GDPR/CCPA user deletion request",
            # NOTE: intentionally not logging any pii
            extra={"user_id": user_id},
        )
        await transaction.commit()

    return None
