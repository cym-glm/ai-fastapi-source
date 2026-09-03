

from fastapi import APIRouter
from app.schemas.response import ApiResponse
from app.schemas.chat import ChatRequest,ChatResponse
from app.services.chat_service import chat_with_ai

router = APIRouter()

# response_model    id name eamil pass 
@router.post("/chat", response_model=ApiResponse)
async def chat(request: ChatRequest) -> ApiResponse:
    res =  await chat_with_ai(request)
    return ApiResponse(
        data=res.model_dump(),
    )
    # return ChatResponse(
    #     answer="Hello, this is a test response",
    #     model=request.model
    # )
