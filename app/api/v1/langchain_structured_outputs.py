from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser
from app.langchain_structured_outputs.schemas import (
    AgentPlanResult,
    IntentClassificationResult,
    RAGAnswerResult,
)
from app.langchain_structured_outputs.service import (
    langchain_structured_output_service,
)


router = APIRouter()


class LCIntentRequest(BaseModel):
    question: str = Field(..., min_length=1)
    provider: str = Field(default="deepseek")
    model: str = Field(default="deepseek-chat")


class LCRAGAnswerRequest(BaseModel):
    question: str = Field(..., min_length=1)
    retrieved_context: str = Field(..., min_length=1)
    provider: str = Field(default="deepseek")
    model: str = Field(default="deepseek-chat")


class LCAgentPlanRequest(BaseModel):
    goal: str = Field(..., min_length=1)
    available_tools: str = Field(..., min_length=1)
    constraints: str = Field(default="无")
    provider: str = Field(default="deepseek")
    model: str = Field(default="deepseek-chat")


@router.post(
    "/langchain/structured/intent",
    response_model=ApiResponse[IntentClassificationResult],
)
async def classify_intent(
    request: LCIntentRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[IntentClassificationResult]:
    result = await langchain_structured_output_service.classify_intent(
        user_question=request.question,
        provider=request.provider,
        model_name=request.model,
    )

    return ApiResponse[IntentClassificationResult](
        data=result
    )


@router.post(
    "/langchain/structured/rag-answer",
    response_model=ApiResponse[RAGAnswerResult],
)
async def rag_answer(
    request: LCRAGAnswerRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[RAGAnswerResult]:
    result = await langchain_structured_output_service.generate_rag_answer(
        user_question=request.question,
        retrieved_context=request.retrieved_context,
        provider=request.provider,
        model_name=request.model,
    )

    return ApiResponse[RAGAnswerResult](
        data=result
    )


@router.post(
    "/langchain/structured/agent-plan",
    response_model=ApiResponse[AgentPlanResult],
)
async def agent_plan(
    request: LCAgentPlanRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[AgentPlanResult]:
    result = await langchain_structured_output_service.plan_agent_task(
        user_goal=request.goal,
        available_tools=request.available_tools,
        constraints=request.constraints,
        provider=request.provider,
        model_name=request.model,
    )

    return ApiResponse[AgentPlanResult](
        data=result
    )