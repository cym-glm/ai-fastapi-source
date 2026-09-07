import asyncio

from app.redis.client import redis_client, close_redis

async  def main():
    pong = await redis_client.ping()
    print("PING:", pong)


    await redis_client.set("course:name", "AI Agent 全栈开发", ex=60)  # 设置过期时间60s 自动删除
    value = await redis_client.get("course:name")
    print("course:name:", value)

    ttl = await redis_client.ttl("course:name") # ttl 剩余时间
    print("ttl:", ttl)

    await close_redis()

asyncio.run(main())