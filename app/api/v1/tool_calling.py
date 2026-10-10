from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.dependencies.llm import get_llm_provider
from app.llm.base import BaseLLMProvider
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser
from app.services.tool_calling_service import tool_calling_service
from app.tools.registry import tool_registry


router = APIRouter()


class ToolCallingRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    model: str = Field(default="deepseek-chat", description="模型名称")


@router.get("/tools", response_model=ApiResponse[list[dict]])
async def list_tools(
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[list[dict]]:
    tools = tool_registry.list_tools()

    return ApiResponse[list[dict]](
        data=[
            {
                "name": tool.name,
                "description": tool.description,
                "enabled": tool.enabled,
                "require_confirm": tool.require_confirm,
                "args_schema": tool.args_schema.model_json_schema(),
                "result_schema": tool.result_schema.model_json_schema(),
            }
            for tool in tools
        ]
    )


@router.post("/tools/run", response_model=ApiResponse[dict])
async def run_tool_calling(
    request: ToolCallingRequest,
    current_user: CurrentUser = Depends(get_current_user),
    llm_provider: BaseLLMProvider = Depends(get_llm_provider),
) -> ApiResponse[dict]:
    result = await tool_calling_service.run_with_tools(
        user_question=request.question,
        model=request.model,
        llm_provider=llm_provider,
    )

    return ApiResponse[dict](
        data=result
    )