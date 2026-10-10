from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.dependencies.llm import get_llm_provider
from app.llm.base import BaseLLMProvider
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser
from app.services.structured_output_service import structured_output_service
from app.structured_outputs.schemas import (
    AgentPlanOutput,
    IntentClassificationOutput,
    RAGStructuredAnswerOutput,
)


router = APIRouter()


class IntentClassificationRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    model: str = Field(default="deepseek-chat", description="模型名称")


class RAGStructuredRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    retrieved_context: str = Field(..., description="检索到的知识库上下文")
    model: str = Field(default="deepseek-chat", description="模型名称")


class AgentPlanRequest(BaseModel):
    goal: str = Field(..., min_length=1, description="用户目标")
    available_tools: str = Field(..., description="可用工具列表")
    constraints: str = Field(default="无", description="约束条件")
    model: str = Field(default="deepseek-chat", description="模型名称")


@router.post(
    "/structured/intent",
    response_model=ApiResponse[IntentClassificationOutput],
)
async def classify_intent(
    request: IntentClassificationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    llm_provider: BaseLLMProvider = Depends(get_llm_provider),
) -> ApiResponse[IntentClassificationOutput]:
    result = await structured_output_service.classify_intent(
        user_question=request.question,
        model=request.model,
        llm_provider=llm_provider,
    )

    return ApiResponse[IntentClassificationOutput](
        data=result
    )


@router.post(
    "/structured/rag-answer",
    response_model=ApiResponse[RAGStructuredAnswerOutput],
)
async def generate_rag_structured_answer(
    request: RAGStructuredRequest,
    current_user: CurrentUser = Depends(get_current_user),
    llm_provider: BaseLLMProvider = Depends(get_llm_provider),
) -> ApiResponse[RAGStructuredAnswerOutput]:
    result = await structured_output_service.generate_rag_answer(
        user_question=request.question,
        retrieved_context=request.retrieved_context,
        model=request.model,
        llm_provider=llm_provider,
    )

    return ApiResponse[RAGStructuredAnswerOutput](
        data=result
    )


@router.post(
    "/structured/agent-plan",
    response_model=ApiResponse[AgentPlanOutput],
)
async def plan_agent(
    request: AgentPlanRequest,
    current_user: CurrentUser = Depends(get_current_user),
    llm_provider: BaseLLMProvider = Depends(get_llm_provider),
) -> ApiResponse[AgentPlanOutput]:
    result = await structured_output_service.plan_agent_task(
        user_goal=request.goal,
        available_tools=request.available_tools,
        constraints=request.constraints,
        model=request.model,
        llm_provider=llm_provider,
    )

    return ApiResponse[AgentPlanOutput](
        data=result
    )