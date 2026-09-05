from fastapi import APIRouter,Depends
from pydantic import BaseModel, Field

from app.core.config import settings

from app.schemas.response import ApiResponse
from app.dependencies.auth import require_admin
from app.schemas.user import CurrentUser


router = APIRouter()


class ModelInfo(BaseModel):
    name: str = Field(..., description="模型名称")
    privider: str = Field(default="mock", description="模型提供商")
    support_stream: bool = Field(default=True, description="是否支持流式输出")

class ModelsResponse(BaseModel):
    models: list[ModelInfo] = Field(default_factory=list, description="模型列表")

@router.get("/models", response_model=ApiResponse[ModelsResponse])
async def list_models(admin_user: CurrentUser = Depends(require_admin)) -> ApiResponse[ModelsResponse]:
    models = [
        ModelInfo(name=model, provider=get_privider_name(model), support_stream=True)
        for model in settings.supported_model_list
    ]
    return ApiResponse[ModelsResponse](data=ModelsResponse(models=models))  


def get_privider_name(model: str) -> str:
    if model.startswith("deepseek"):
        return "deepseek"
    if model.startswith("qwen"):
        return "qwen"
    if model.startswith("gpt"):
        return "openai"
    return "unknown"
