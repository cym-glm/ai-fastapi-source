
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.deepagents_context.service import deepagents_context_service
from app.schemas.response import ApiResponse


router = APIRouter()


class ContextDemoApiRequest(BaseModel):
    user_goal: str = Field(..., min_length=1)
    user_id: str = Field(default="anonymous")
    max_tokens: int = Field(default=3000, ge=1000, le=20000)


@router.post(
    "/deepagents/context/run-demo",
    response_model=ApiResponse[dict],
)
async def run_context_demo(
    request: ContextDemoApiRequest,
) -> ApiResponse[dict]:
    result = deepagents_context_service.run_demo(
        user_goal=request.user_goal,
        user_id=request.user_id,
        max_tokens=request.max_tokens,
    )

    return ApiResponse[dict](
        data=result
    )


@router.get(
    "/deepagents/context/files",
    response_model=ApiResponse[list[str]],
)
async def list_files() -> ApiResponse[list[str]]:
    return ApiResponse[list[str]](
        data=deepagents_context_service.list_files()
    )


@router.get(
    "/deepagents/context/files/read",
    response_model=ApiResponse[dict],
)
async def read_file(
    file_path: str,
) -> ApiResponse[dict]:
    content = deepagents_context_service.read_file(
        file_path=file_path
    )

    return ApiResponse[dict](
        data={
            "file_path": file_path,
            "content": content,
        }
    )


@router.post(
    "/deepagents/context/clear",
    response_model=ApiResponse[dict],
)
async def clear_workspace() -> ApiResponse[dict]:
    deepagents_context_service.clear_workspace()

    return ApiResponse[dict](
        data={
            "message": "workspace cleared"
        }
    )