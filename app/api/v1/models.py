from fastapi import APIRouter,Depends
from pydantic import BaseModel, Field

from app.core.config import settings

from app.schemas.response import ApiResponse
from app.dependencies.auth import require_admin
from app.schemas.user import CurrentUser


router = APIRouter()


# class ModelInfo(BaseModel):
#     name: str = Field(..., description="模型名称")
#     privider: str = Field(default="mock", description="模型提供商")
#     support_stream: bool = Field(default=True, description="是否支持流式输出")

# class ModelsResponse(BaseModel):
#     models: list[ModelInfo] = Field(default_factory=list, description="模型列表")


@router.get("/models", response_model=ApiResponse[list[dict]])
async def list_models() -> ApiResponse[list[dict]]:
    models = []

    for model_name in settings.supported_models.split(","):
        model_name = model_name.strip()

        if not model_name:
            continue

        if model_name.startswith("deepseek"):
            provider = "deepseek"
        elif model_name.startswith("qwen"):
            provider = "qwen"
        elif model_name.startswith("gpt"):
            provider = "openai"
        else:
            provider = "unknown"

        models.append(
            {
                "model": model_name,
                "provider": provider,
                "support_stream": True,
                "support_tools": provider in ["deepseek", "qwen", "openai"],
            }
        )

    return ApiResponse[list[dict]](
        data=models
    )

# def get_privider_name(model: str) -> str:
#     if model.startswith("deepseek"):
#         return "deepseek"
#     if model.startswith("qwen"):
#         return "qwen"
#     if model.startswith("gpt"):
#         return "openai"
#     return "unknown"
