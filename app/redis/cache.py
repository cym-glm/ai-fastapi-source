
import json
import hashlib
from redis.asyncio import Redis
from app.core.config import settings
from app.redis.keys import (
    api_key_cache_key,
    chat_response_cache_key,
    conversation_recent_messages_key,
    rate_limit_key,
)
from app.schemas.chat import ChatMessage, MessageRole

async def cache_recent_messages(
    redis: Redis,
    conversation_id: str,
    messages: list[ChatMessage],
    ttl_seconds: int| None = None,
):
    key = conversation_recent_messages_key(conversation_id)
    data = [
        {"role": message.role, "content": message.content}
        for message in messages
    ]

    await redis.set(key, json.dumps(data, ensure_ascii=False),
                ex= ttl_seconds or settings.redis_default_ttl_seconds)

async def get_cached_recent_messages(
        redis: Redis,
        conversation_id: str,
) -> list[ChatMessage] | None:
    key = conversation_recent_messages_key(conversation_id)
    value = await redis.get(key)
    if not value:
        return None
    data = json.loads(value)
    return [
        ChatMessage(
            role=MessageRole(item["role"]),
            content=item["content"],
        )
        for item in data
    ]


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

async def get_cached_chat_response(
        redis: Redis,
        question: str,
) -> str | None:
    key = chat_response_cache_key(hash_text(question))
    return await redis.get(key)

async def cache_chat_response(
        redis: Redis,
        question: str,
        answer: str,
        ttl_seconds: int = 300,
):
    key = chat_response_cache_key(hash_text(question))
    await redis.set(key, answer, ex= ttl_seconds)