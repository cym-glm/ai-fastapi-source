from fastapi import Depends, HTTPException, status
from redis.asyncio import Redis

from app.dependencies.auth import get_current_user
from app.dependencies.redis import get_redis_client
from app.redis.rate_limit import check_rate_limit
from app.schemas.user import CurrentUser


async def chat_rate_limit(
    current_user: CurrentUser = Depends(get_current_user),
    redis: Redis = Depends(get_redis_client),
):
    allowed, current, ttl = await check_rate_limit(
        redis=redis,
        user_id=current_user.user_id,
        api_name="chat",
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"请求太频繁，请 {ttl} 秒后再试。当前窗口请求次数：{current}",
        )