import uuid

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException, ErrorCode
from app.core.logging import get_logger
from app.llm.base import BaseLLMProvider
from app.llm.errors import LLMProviderError
from app.llm.factory import LLMProviderFactory
from app.llm.schemas import LLMMessage, LLMRequest, LLMRole
from app.redis.cache import cache_chat_response, get_cached_chat_response
from app.repositories.conversation_repository import conversation_repository
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    MessageRole,
    SourceDocument,
    TokenUsage,
)


logger = get_logger(__name__)


async def chat_with_ai(
    request: ChatRequest,
    db: AsyncSession | None = None,
    redis: Redis | None = None,
    llm_provider: BaseLLMProvider | None = None,
) -> ChatResponse:
    latest_user_message = get_latest_user_message(request)
    model = request.model or settings.default_model

    logger.info(
        f"chat_start model={model} message_count={len(request.messages)}"
    )

    if redis:
        cached_answer = await get_cached_chat_response(
            redis=redis,
            question=latest_user_message,
        )

        if cached_answer:
            logger.info("chat_response_cache_hit")

            return ChatResponse(
                answer=cached_answer,
                model=model,
                session_id=request.session_id,
                message_id=f"m_{uuid.uuid4().hex[:8]}",
                usage=TokenUsage(),
                sources=[],
                trace_id=f"trace_{uuid.uuid4().hex[:8]}",
            )


    llm_provider = llm_provider or LLMProviderFactory.create()

    llm_request = build_llm_request_from_chat_request(request)

    try:
        llm_response = await llm_provider.chat(llm_request)
    except LLMProviderError as exc:
        logger.exception(
            f"chat_llm_provider_error provider={exc.provider} "
            f"status_code={exc.status_code}"
        )
        raise AppException(
            message=exc.message,
            code=ErrorCode.LLM_CALL_FAILED,
            status_code=500,
            data={
                "provider": exc.provider,
                "status_code": exc.status_code,
            },
        ) from exc

    answer = llm_response.content

    usage = TokenUsage(
        prompt_tokens=llm_response.usage.prompt_tokens,
        completion_tokens=llm_response.usage.completion_tokens,
        total_tokens=llm_response.usage.total_tokens,
    )

    if redis:
        await cache_chat_response(
            redis=redis,
            question=latest_user_message,
            answer=answer,
        )

    if db and request.session_id:
        await conversation_repository.add_message(
            db=db,
            conversation_id=request.session_id,
            role=MessageRole.USER.value,
            content=latest_user_message,
            model=model,
            prompt_tokens=usage.prompt_tokens,
        )

        await conversation_repository.add_message(
            db=db,
            conversation_id=request.session_id,
            role=MessageRole.ASSISTANT.value,
            content=answer,
            model=model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )

    logger.info(
        f"chat_success model={model} answer_length={len(answer)} "
        f"total_tokens={usage.total_tokens}"
    )

    return ChatResponse(
        answer=answer,
        model=model,
        session_id=request.session_id or f"s_{uuid.uuid4().hex[:8]}",
        message_id=f"m_{uuid.uuid4().hex[:8]}",
        usage=usage,
        sources=build_mock_sources(latest_user_message),
        trace_id=f"trace_{uuid.uuid4().hex[:8]}",
    )


def build_llm_request_from_chat_request(request: ChatRequest) -> LLMRequest:
    return LLMRequest(
        model=request.model,
        messages=[
            LLMMessage(
                role=LLMRole(message.role.value),
                content=message.content,
            )
            for message in request.messages
        ],
        temperature=request.temperature,
        stream=request.stream,
    )


def get_latest_user_message(request: ChatRequest) -> str:
    for message in reversed(request.messages):
        if message.role == MessageRole.USER:
            return message.content

    return request.messages[-1].content


def build_mock_sources(question: str) -> list[SourceDocument]:
    if "RAG" not in question and "知识库" not in question:
        return []

    return [
        SourceDocument(
            document_id="doc_001",
            title="企业知识库说明文档",
            content="RAG 是 Retrieval Augmented Generation，用于结合外部知识增强大模型回答。",
            score=0.89,
            metadata={
                "source": "mock",
                "page": 1,
            },
        )
    ]