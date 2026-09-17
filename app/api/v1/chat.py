

from fastapi import APIRouter, Path,Query, Body,Depends, Request
from fastapi.responses import StreamingResponse
from app.schemas.response import ApiResponse
from app.schemas.chat import ChatRequest,ChatResponse,GenerateTitleRequest, GenerateTitleResponse
from app.services.chat_service import chat_with_ai
from app.dependencies.auth import get_current_user
from app.dependencies.llm import get_llm_provider, MockLLMProvider
from app.schemas.user import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from redis.asyncio import Redis
from app.dependencies.redis import get_redis_client
from app.llm.base import BaseLLMProvider
from app.dependencies.llm import get_llm_provider
from app.services.chat_stream_service import stream_chat_with_ai
router = APIRouter()

# response_model    id name eamil pass 
@router.post("/chat", response_model=ApiResponse)
async def chat(
    request: ChatRequest, 
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis= Depends(get_redis_client),
    llm_provider: BaseLLMProvider = Depends(get_llm_provider)
    ) -> ApiResponse:
        res =  await chat_with_ai(request, db, redis, llm_provider)
        res.trace_id = f"{res.trace_id}_user_{current_user.user_id}"
        return ApiResponse[ChatResponse](
            data=res
        )
        # return ChatResponse(
        #     answer="Hello, this is a test response",
        #     model=request.model
        # )


@router.post("/conversations/{conversation_id}/chat", response_model=ApiResponse[ChatResponse])
async def chat_in_conversation(
    request: ChatRequest,
    conversation_id: str= Path(..., description="会话ID"), # path 参数
    debug: bool = Query(default=False, description="是否开启调试模式")
) -> ApiResponse[ChatResponse]:
    res =  await chat_with_ai(request)
    if debug:
        res.trace_id = res.trace_id or "debug_trace"

    res.session_id = conversation_id
    return ApiResponse[ChatResponse](
        data=res
    )




@router.post("/title", response_model=ApiResponse[GenerateTitleResponse])
async def title(request: GenerateTitleRequest) -> ApiResponse[GenerateTitleResponse]:
    title = request.title[:20]
    return ApiResponse[GenerateTitleResponse](
        data= GenerateTitleResponse(title=title)
    )


@router.post("/chat/di-demo", response_model=ApiResponse[ChatResponse])
async def chat_di_demo(
        request: ChatRequest,
        current_user: CurrentUser = Depends(get_current_user),
        llm_provider: MockLLMProvider = Depends(get_llm_provider)
) ->ApiResponse[ChatResponse]:
    latest_message = request.messages[-1].content

    answer = await llm_provider.chat(
        message=f"用户 {current_user.username} 问：{latest_message}"
    )

    result = ChatResponse(
        answer=answer,
        model=llm_provider.model,
        session_id=request.session_id,
    )

    return ApiResponse[ChatResponse](
        data=result
    )



@router.post(
    "/chat/stream",
)
async def chat_stream(
    request_body: ChatRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
    llm_provider: BaseLLMProvider = Depends(get_llm_provider),
):
    async def event_generator():
        async for event in stream_chat_with_ai(
            request=request_body,
            llm_provider=llm_provider,
            db=db,
            redis=redis,
        ):
            if await request.is_disconnected():
                break

            yield event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )



# @router.post("/title")
# async def title(message: str = Body(..., embed=True, min_length=1,description="消息内容") ):
#     return {
#         "title": message[:20]
#     }