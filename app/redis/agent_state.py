import json
from typing import Any

from redis.asyncio import Redis

from app.redis.keys import agent_run_state_key


async def set_agent_run_state(
    redis: Redis,
    run_id: str,
    state: dict[str, Any],
    ttl_seconds: int = 3600,
):
    key = agent_run_state_key(run_id)

    await redis.set(
        key,
        json.dumps(state, ensure_ascii=False),
        ex=ttl_seconds,
    )


async def get_agent_run_state(
    redis: Redis,
    run_id: str,
) -> dict[str, Any] | None:
    key = agent_run_state_key(run_id)
    value = await redis.get(key)

    if not value:
        return None

    return json.loads(value)