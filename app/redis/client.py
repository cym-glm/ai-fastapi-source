


import redis.asyncio as redis

from app.core.config import settings

redis_client = redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True, # 表示redis返回的字符串是utf-8编码 而不是字节流 bytes
    # b"hello"       hello 
    )
async def close_redis():
    await redis_client.aclose()