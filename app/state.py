from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from databases import Database
    from redis.asyncio import Redis
    from types_aiobotocore_s3.client import S3Client

database: "Database"
redis: "Redis"
s3_client: "S3Client"
