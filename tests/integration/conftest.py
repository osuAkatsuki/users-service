import os
from collections.abc import AsyncIterator

import pytest
from databases import Database

import app.state

# Mirrors the production (Ripple-lineage) definition of the table.
CREATE_PASSWORD_RECOVERY_TABLE = """\
    CREATE TABLE password_recovery (
        id INT NOT NULL AUTO_INCREMENT,
        k VARCHAR(80) NOT NULL,
        u VARCHAR(30) NOT NULL,
        t TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id)
    )
"""


@pytest.fixture
async def database() -> AsyncIterator[Database]:
    dsn = os.environ.get("TEST_DB_DSN")
    if not dsn:
        pytest.skip(
            "TEST_DB_DSN is not set "
            "(e.g. mysql+aiomysql://user:pass@localhost:3306/users_service_test)",
        )

    db = Database(dsn)
    try:
        await db.connect()
    except Exception as exc:
        pytest.skip(f"could not connect to TEST_DB_DSN: {exc!r}")

    # Recreate from scratch each test: a pristine schema, and individual tests
    # may safely ALTER the table (e.g. to exercise a nullable `t`).
    await db.execute("DROP TABLE IF EXISTS password_recovery")
    await db.execute(CREATE_PASSWORD_RECOVERY_TABLE)
    app.state.database = db
    try:
        yield db
    finally:
        await db.disconnect()
