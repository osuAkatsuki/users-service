from databases import Database

from app import security
from app.repositories import password_reset_tokens
from app.repositories.password_reset_tokens import PASSWORD_RESET_TOKEN_TTL_SECONDS


def make_hashed_token() -> str:
    return security.hash_secure_token(security.generate_unhashed_secure_token())


async def age_token(database: Database, hashed_token: str, age_seconds: int) -> None:
    """Backdate a token's creation time on the DB clock (no wall-clock sleeps)."""
    query = """\
        UPDATE password_recovery
        SET t = NOW() - INTERVAL :age_seconds SECOND
        WHERE k = :hashed_token
    """
    params = {"age_seconds": age_seconds, "hashed_token": hashed_token}
    await database.execute(query, params)


async def count_tokens(database: Database, hashed_token: str) -> int:
    query = """\
        SELECT COUNT(*) AS cnt
        FROM password_recovery
        WHERE k = :hashed_token
    """
    rec = await database.fetch_one(query, {"hashed_token": hashed_token})
    assert rec is not None
    return int(rec["cnt"])


async def test_create_stamps_creation_time_with_db_clock(database: Database) -> None:
    hashed_token = make_hashed_token()
    await password_reset_tokens.create(username="cmyui", hashed_token=hashed_token)

    query = """\
        SELECT TIMESTAMPDIFF(SECOND, t, NOW()) AS age_seconds
        FROM password_recovery
        WHERE k = :hashed_token
    """
    rec = await database.fetch_one(query, {"hashed_token": hashed_token})
    assert rec is not None
    assert 0 <= rec["age_seconds"] <= 30


async def test_fresh_token_is_valid(database: Database) -> None:
    hashed_token = make_hashed_token()
    await password_reset_tokens.create(username="cmyui", hashed_token=hashed_token)

    result = await password_reset_tokens.fetch_one(hashed_token)

    assert result is not None
    assert result.username == "cmyui"
    assert result.hashed_token == hashed_token


async def test_missing_token_is_rejected(database: Database) -> None:
    result = await password_reset_tokens.fetch_one(make_hashed_token())

    assert result is None


async def test_token_older_than_ttl_is_rejected(database: Database) -> None:
    hashed_token = make_hashed_token()
    await password_reset_tokens.create(username="cmyui", hashed_token=hashed_token)
    await age_token(database, hashed_token, PASSWORD_RESET_TOKEN_TTL_SECONDS + 60)

    result = await password_reset_tokens.fetch_one(hashed_token)

    assert result is None


async def test_expired_token_is_deleted_on_read(database: Database) -> None:
    hashed_token = make_hashed_token()
    await password_reset_tokens.create(username="cmyui", hashed_token=hashed_token)
    await age_token(database, hashed_token, PASSWORD_RESET_TOKEN_TTL_SECONDS + 60)

    await password_reset_tokens.fetch_one(hashed_token)

    assert await count_tokens(database, hashed_token) == 0


async def test_token_at_exactly_ttl_is_expired(database: Database) -> None:
    # The boundary is inclusive: a token exactly TTL seconds old is expired
    # (tokens are valid strictly for less than the TTL).
    hashed_token = make_hashed_token()
    await password_reset_tokens.create(username="cmyui", hashed_token=hashed_token)
    await age_token(database, hashed_token, PASSWORD_RESET_TOKEN_TTL_SECONDS)

    result = await password_reset_tokens.fetch_one(hashed_token)

    assert result is None


async def test_token_just_inside_ttl_is_valid(database: Database) -> None:
    # A 5 minute margin keeps this deterministic on slow test runs.
    hashed_token = make_hashed_token()
    await password_reset_tokens.create(username="cmyui", hashed_token=hashed_token)
    await age_token(database, hashed_token, PASSWORD_RESET_TOKEN_TTL_SECONDS - 300)

    result = await password_reset_tokens.fetch_one(hashed_token)

    assert result is not None


async def test_token_one_second_under_ttl_is_valid(database: Database) -> None:
    # Tightest valid boundary: age == TTL - 1s. Rule is "valid iff age < TTL".
    hashed_token = make_hashed_token()
    await password_reset_tokens.create(username="cmyui", hashed_token=hashed_token)
    await age_token(database, hashed_token, PASSWORD_RESET_TOKEN_TTL_SECONDS - 1)

    result = await password_reset_tokens.fetch_one(hashed_token)

    assert result is not None


async def test_token_one_second_over_ttl_is_expired(database: Database) -> None:
    # Tightest expired boundary: age == TTL + 1s.
    hashed_token = make_hashed_token()
    await password_reset_tokens.create(username="cmyui", hashed_token=hashed_token)
    await age_token(database, hashed_token, PASSWORD_RESET_TOKEN_TTL_SECONDS + 1)

    result = await password_reset_tokens.fetch_one(hashed_token)

    assert result is None


async def test_ancient_timestamp_fails_safe_as_expired(database: Database) -> None:
    # A degenerate/legacy `t` far in the past must fail safe (rejected + purged),
    # never accepted. This is the "zero/garbage timestamp" direction.
    hashed_token = make_hashed_token()
    await password_reset_tokens.create(username="cmyui", hashed_token=hashed_token)
    query = """\
        UPDATE password_recovery
        SET t = '2000-01-01 00:00:00'
        WHERE k = :hashed_token
    """
    await database.execute(query, {"hashed_token": hashed_token})

    result = await password_reset_tokens.fetch_one(hashed_token)

    assert result is None
    assert await count_tokens(database, hashed_token) == 0


async def test_null_timestamp_fails_closed(database: Database) -> None:
    # The production column is NOT NULL, so this cannot occur there; prove the
    # defense-in-depth path anyway against a real DB by making `t` nullable for
    # this row. A NULL age must fail closed (rejected + purged), never accepted.
    await database.execute("ALTER TABLE password_recovery MODIFY t TIMESTAMP NULL")
    hashed_token = make_hashed_token()
    query = """\
        INSERT INTO password_recovery (k, u, t)
        VALUES (:hashed_token, :username, NULL)
    """
    await database.execute(query, {"hashed_token": hashed_token, "username": "cmyui"})

    result = await password_reset_tokens.fetch_one(hashed_token)

    assert result is None
    assert await count_tokens(database, hashed_token) == 0
