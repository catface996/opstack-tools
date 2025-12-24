"""Redis connection management."""

from redis.asyncio import Redis, from_url

from aiops_tools.core.config import settings

# Redis client instance
redis_client: Redis | None = None


async def get_redis() -> Redis:
    """Get Redis client instance."""
    global redis_client
    if redis_client is None:
        redis_client = await from_url(
            str(settings.redis_url),
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None
