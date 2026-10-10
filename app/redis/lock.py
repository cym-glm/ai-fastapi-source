import uuid

from redis.asyncio import Redis

from app.redis.keys import lock_key


async def acquire_lock(
    redis: Redis,
    resource: str,
    resource_id: str,
    ttl_seconds: int = 30,
) -> str | None:
    key = lock_key(resource, resource_id)
    token = str(uuid.uuid4())

    success = await redis.set(
        key,
        token,
        ex=ttl_seconds,
        nx=True,
    )

    if success:
        return token

    return None


async def release_lock(
    redis: Redis,
    resource: str,
    resource_id: str,
    token: str,
) -> bool:
    key = lock_key(resource, resource_id)

    current_token = await redis.get(key)

    if current_token != token:
        return False

    await redis.delete(key)
    return True