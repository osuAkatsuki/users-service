from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from databases import Database
    from redis.asyncio import Redis

database: "Database"
redis: "Redis"
