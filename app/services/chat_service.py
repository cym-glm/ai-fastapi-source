
import asyncio
from fastapi import HTTPException
from app.schemas.chat import ChatRequest, ChatResponse

async def chat_with_ai(request: ChatRequest) -> ChatResponse:
    await asyncio.sleep(1)

    # supported_models = ["gpt-3.5-turbo", "gpt-4", "deepseek-chat", "qwen-72e"]

    # if request.model not in supported_models:
    #     raise HTTPException(status_code=400, detail=f"Unsupported model{request.model}")
    if "AI Agent" in request.message:
        answer= ("AI Agent 可以理解您的请求，请问您需要我做什么？")
    elif "RAG" in request.message:
        answer=("RAG 可以帮助您从大量数据中快速找到所需信息，请问您需要查找什么内容？")
    else: 
        answer=("对不起，我不明白您的请求。请问您需要我做什么？")
    return ChatResponse(
        answer=answer,
        model=request.model
    )

