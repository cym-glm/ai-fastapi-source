from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.deepagents_core.service import deep_agent_core_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()


class DeepAgentRunApiRequest(BaseModel):
    user_request: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")
    thread_id: str | None = None


@router.post(
    "/deepagents/core/run",
    response_model=ApiResponse[dict],
)
async def run_deep_agent(
    request: DeepAgentRunApiRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = deep_agent_core_service.run_task(
        user_request=request.user_request,
        tenant_id=request.tenant_id,
        user_id=current_user.user_id,
        thread_id=request.thread_id,
    )

    return ApiResponse[dict](
        data=result
    )


@router.get(
    "/deepagents/core/files",
    response_model=ApiResponse[list[str]],
)
async def list_files(
    thread_id: str,
) -> ApiResponse[list[str]]:
    files = deep_agent_core_service.list_workspace_files(
        thread_id=thread_id,
    )

    return ApiResponse[list[str]](
        data=files
    )


@router.get(
    "/deepagents/core/files/read",
    response_model=ApiResponse[dict],
)
async def read_file(
    thread_id: str,
    file_path: str,
) -> ApiResponse[dict]:
    content = deep_agent_core_service.read_workspace_file(
        thread_id=thread_id,
        file_path=file_path,
    )

    return ApiResponse[dict](
        data={
            "thread_id": thread_id,
            "file_path": file_path,
            "content": content,
        }
    )