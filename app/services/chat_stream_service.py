import uuid
from collections.abc import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ErrorCode
from app.core.logging import get_logger
from app.llm.base import BaseLLMProvider
from app.llm.errors import LLMProviderError
from app.llm.schemas import LLMRequest
from app.redis.cache import cache_chat_response, get_cached_chat_response
from app.schemas.chat import ChatRequest, MessageRole, TokenUsage
from app.services.chat_service import (
    build_llm_request_from_chat_request,
    get_latest_user_message,
    save_chat_messages,
)
from app.utils.sse import format_done_event, format_error_event, format_sse


logger = get_logger(__name__)


async def stream_chat_with_ai(
    request: ChatRequest,
    llm_provider: BaseLLMProvider,
    db: AsyncSession | None = None,
    redis: Redis | None = None,
) -> AsyncGenerator[str, None]:
    latest_user_message = get_latest_user_message(request)

    llm_request: LLMRequest = build_llm_request_from_chat_request(request)
    llm_request.stream = True

    message_id = f"m_{uuid.uuid4().hex[:8]}"
    full_answer = ""
    final_usage = TokenUsage()

    logger.info(
        f"chat_stream_start model={llm_request.model} "
        f"session_id={request.session_id}"
    )

    if redis:
        cached_answer = await get_cached_chat_response(
            redis=redis,
            question=latest_user_message,
        )

        if cached_answer:
            yield format_sse(
                event="start",
                data={
                    "message_id": message_id,
                    "model": llm_request.model,
                    "session_id": request.session_id,
                    "cache_hit": True,
                },
            )

            for part in split_text(cached_answer, size=8):
                yield format_sse(
                    event="message",
                    data={
                        "content": part,
                        "message_id": message_id,
                        "cache_hit": True,
                    },
                )

            yield format_done_event(
                {
                    "message_id": message_id,
                    "finish_reason": "cache_hit",
                    "usage": final_usage.model_dump(),
                }
            )

            return

    yield format_sse(
        event="start",
        data={
            "message_id": message_id,
            "model": llm_request.model,
            "session_id": request.session_id,
            "cache_hit": False,
        },
    )

    try:
        async for chunk in llm_provider.stream_chat(llm_request):
            if chunk.content:
                full_answer += chunk.content

                yield format_sse(
                    event="message",
                    data={
                        "content": chunk.content,
                        "message_id": message_id,
                    },
                )

            if chunk.usage:
                final_usage = TokenUsage(
                    prompt_tokens=chunk.usage.prompt_tokens,
                    completion_tokens=chunk.usage.completion_tokens,
                    total_tokens=chunk.usage.total_tokens,
                )

        if redis and full_answer:
            await cache_chat_response(
                redis=redis,
                question=latest_user_message,
                answer=full_answer,
            )

        if db and request.session_id:
            await save_chat_messages(
                db=db,
                conversation_id=request.session_id,
                user_message=latest_user_message,
                assistant_message=full_answer,
                model=llm_request.model,
                usage=final_usage,
            )

        logger.info(
            f"chat_stream_success model={llm_request.model} "
            f"answer_length={len(full_answer)} "
            f"total_tokens={final_usage.total_tokens}"
        )

        yield format_done_event(
            {
                "message_id": message_id,
                "finish_reason": "stop",
                "usage": final_usage.model_dump(),
            }
        )

    except LLMProviderError as exc:
        logger.exception(
            f"chat_stream_llm_error provider={exc.provider} "
            f"status_code={exc.status_code}"
        )

        yield format_error_event(
            message=exc.message,
            code=int(ErrorCode.LLM_CALL_FAILED),
            detail={
                "provider": exc.provider,
                "status_code": exc.status_code,
            },
        )

    except Exception as exc:
        logger.exception(
            f"chat_stream_unhandled_error error={repr(exc)}"
        )

        yield format_error_event(
            message="流式输出失败",
            code=int(ErrorCode.INTERNAL_ERROR),
        )


def split_text(text: str, size: int = 8) -> list[str]:
    return [
        text[index:index + size]
        for index in range(0, len(text), size)
    ]