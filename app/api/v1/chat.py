

from fastapi import APIRouter, Path,Query, Body,Depends
from app.schemas.response import ApiResponse
from app.schemas.chat import ChatRequest,ChatResponse,GenerateTitleRequest, GenerateTitleResponse
from app.services.chat_service import chat_with_ai
from app.dependencies.auth import get_current_user
from app.dependencies.llm import get_llm_provider, MockLLMProvider
from app.schemas.user import CurrentUser

router = APIRouter()

# response_model    id name eamil pass 
@router.post("/chat", response_model=ApiResponse)
async def chat(
    request: ChatRequest, 
    current_user: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    res =  await chat_with_ai(request)
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


# @router.post("/title")
# async def title(message: str = Body(..., embed=True, min_length=1,description="消息内容") ):
#     return {
#         "title": message[:20]
#     }

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

