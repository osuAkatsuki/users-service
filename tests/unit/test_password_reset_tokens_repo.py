from datetime import datetime
from typing import Any

import pytest

import app.state
from app.repositories import password_reset_tokens


class FakeDatabase:
    def __init__(self) -> None:
        self.fetch_one_results: list[Any] = []
        self.fetch_one_calls: list[tuple[str, dict[str, Any] | None]] = []
        self.execute_calls: list[tuple[str, dict[str, Any] | None]] = []

    async def fetch_one(
        self,
        query: str,
        values: dict[str, Any] | None = None,
    ) -> Any:
        self.fetch_one_calls.append((query, values))
        return self.fetch_one_results.pop(0)

    async def execute(
        self,
        query: str,
        values: dict[str, Any] | None = None,
    ) -> Any:
        self.execute_calls.append((query, values))
        return None


@pytest.fixture
def fake_database(monkeypatch: pytest.MonkeyPatch) -> FakeDatabase:
    fake = FakeDatabase()
    monkeypatch.setattr(app.state, "database", fake, raising=False)
    return fake


async def test_fetch_one_returns_none_for_missing_token(
    fake_database: FakeDatabase,
) -> None:
    fake_database.fetch_one_results.append(None)

    result = await password_reset_tokens.fetch_one("missing-token-hash")

    assert result is None
    assert fake_database.execute_calls == []


async def test_fetch_one_returns_fresh_token_and_keeps_row(
    fake_database: FakeDatabase,
) -> None:
    fake_database.fetch_one_results.append(
        {
            "id": 1,
            "u": "cmyui",
            "t": datetime(2026, 7, 7, 12, 0, 0),
            "is_valid": 1,
        },
    )

    result = await password_reset_tokens.fetch_one("fresh-token-hash")

    assert result is not None
    assert result.hashed_token == "fresh-token-hash"
    assert result.username == "cmyui"
    assert fake_database.execute_calls == []

    query, params = fake_database.fetch_one_calls[0]
    assert params is not None
    # expiry must be judged on the DB clock, not the application clock
    assert "TIMESTAMPDIFF" in query
    assert "NOW()" in query
    ttl = password_reset_tokens.PASSWORD_RESET_TOKEN_TTL_SECONDS
    assert params["ttl_seconds"] == ttl


async def test_fetch_one_rejects_and_deletes_expired_token(
    fake_database: FakeDatabase,
) -> None:
    fake_database.fetch_one_results.append(
        {
            "id": 1,
            "u": "cmyui",
            "t": datetime(2026, 7, 7, 12, 0, 0),
            "is_valid": 0,
        },
    )

    result = await password_reset_tokens.fetch_one("expired-token-hash")

    assert result is None
    assert len(fake_database.execute_calls) == 1
    query, params = fake_database.execute_calls[0]
    assert "DELETE FROM password_recovery" in query
    assert params == {"hashed_token": "expired-token-hash"}


async def test_fetch_one_fails_closed_when_validity_is_null(
    fake_database: FakeDatabase,
) -> None:
    # A NOT NULL `t` should never yield a NULL age, but a corrupted/migrated row
    # must fail closed (rejected + deleted), never silently accepted.
    fake_database.fetch_one_results.append(
        {
            "id": 1,
            "u": "cmyui",
            "t": datetime(2026, 7, 7, 12, 0, 0),
            "is_valid": None,
        },
    )

    result = await password_reset_tokens.fetch_one("corrupt-token-hash")

    assert result is None
    assert len(fake_database.execute_calls) == 1
    query, params = fake_database.execute_calls[0]
    assert "DELETE FROM password_recovery" in query
    assert params == {"hashed_token": "corrupt-token-hash"}


async def test_create_writes_creation_time_explicitly(
    fake_database: FakeDatabase,
) -> None:
    fake_database.fetch_one_results.append(
        {
            "id": 1,
            "k": "token-hash",
            "u": "cmyui",
            "t": datetime(2026, 7, 7, 12, 0, 0),
        },
    )

    result = await password_reset_tokens.create(
        username="cmyui",
        hashed_token="token-hash",
    )

    assert result.created_at == datetime(2026, 7, 7, 12, 0, 0)
    insert_query, insert_params = fake_database.execute_calls[0]
    assert "INSERT INTO password_recovery (k, u, t)" in insert_query
    assert "NOW()" in insert_query
    assert insert_params == {"hashed_token": "token-hash", "username": "cmyui"}
