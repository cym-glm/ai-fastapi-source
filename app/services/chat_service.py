
import asyncio
import uuid
from fastapi import HTTPException
from app.core.config import settings
from app.core.exceptions import AppException, ErrorCode
from app.schemas.chat import ChatRequest, ChatResponse, TokenUsage, SourceDocument,MessageRole
from app.core.logging import get_logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.conversation_repository import conversation_repository

logger = get_logger(__name__)

async def chat_with_ai(
        request: ChatRequest,
        db: AsyncSession | None= None) -> ChatResponse:
    await asyncio.sleep(1)

    # supported_models = ["gpt-3.5-turbo", "gpt-4", "deepseek-chat", "qwen-72e"]

    # if request.model not in supported_models:
    #     raise HTTPException(status_code=400, detail=f"Unsupported model{request.model}")

    latest_user_message = get_latest_user_message(request)

    model = request.model or settings.default_model
    answer = ""
    logger.info(f"chat_with_ai 收到用户请求，模型为{model}，answer_length={len(answer)}")

    if"触发业务异常" in latest_user_message:
        raise  AppException(
            message="触发业务异常",
            code=ErrorCode.LLM_CALL_FAILED,
            status_code=500,
            data={"model": f"{request.model}  llm failed"}
        )
    if "AI Agent" in latest_user_message:
        answer= ("AI Agent 可以理解您的请求，请问您需要我做什么？")
    elif "RAG" in latest_user_message:
        answer=("RAG 可以帮助您从大量数据中快速找到所需信息，请问您需要查找什么内容？")
    elif "LangGraph" in latest_user_message:
        answer=("LangGraph 可以帮助您理解复杂的概念和关系，请问您需要了解什么内容？")
    else: 
        answer=("对不起，我不明白您的请求。请问您需要我做什么？")

    logger.info(
        f"chat_success model={model} answer_length={len(answer)}"
    )

    usage = TokenUsage(
        prompt_tokens=count_tokens_from_messages(request),
        completion_tokens=len(answer),
        total_tokens=count_tokens_from_messages(request) + len(answer)
    )

    source =  build_sources(latest_user_message)

    # 调用数据库层 
    if db and request.session_id:
        await conversation_repository.add_message(
            db=db, 
            conversation_id=request.session_id,
            role=MessageRole.USER.value,
            content=latest_user_message,
            model=request.model)
        await conversation_repository.add_message(
            db=db, 
            conversation_id=request.session_id,
            role=MessageRole.ASSISTANT.value,
            content=answer,
            model=request.model)
        
    return ChatResponse(
        answer=answer,
        model=model,
        session_id=request.session_id or f"s_{uuid.uuid4().hex}",
        message_id=f"m_{uuid.uuid4().hex[:8]}",
        usage=usage,
        sources=source,
        trace_id=f"trae_{uuid.uuid4().hex[:8]}"

    )



def get_latest_user_message(request: ChatRequest) -> str:
    for message in reversed(request.messages):
        if message.role == MessageRole.USER:
            return message.content
    return request.messages[-1].content


def count_tokens_from_messages(request: ChatRequest) -> int:
    return sum(len(message.content) for message in request.messages )


def build_sources(question: str) -> list[SourceDocument]:
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
        ),
        SourceDocument(document_id="2", title=question, content=question, score=0.8),
        SourceDocument(document_id="3", title=question, content=question, score=0.7),
    ]

# def build_response(answer: str, usage: TokenUsage, sources: list[SourceDomcument]) -> ChatResponse:
#     return ChatResponse(
#         answer=answer,
#         usage=usage,
#         sources=sources
#     )