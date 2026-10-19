from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.deepagents_subagent.service import deepagents_subagent_service
from app.schemas.response import ApiResponse


router = APIRouter()


class RunSubAgentFlowApiRequest(BaseModel):
    user_goal: str = Field(..., min_length=1)


@router.get(
    "/deepagents/subagents",
    response_model=ApiResponse[list[dict]],
)
async def list_subagents() -> ApiResponse[list[dict]]:
    return ApiResponse[list[dict]](
        data=deepagents_subagent_service.list_subagents()
    )


@router.post(
    "/deepagents/subagents/run",
    response_model=ApiResponse[dict],
)
async def run_subagent_flow(
    request: RunSubAgentFlowApiRequest,
) -> ApiResponse[dict]:
    result = deepagents_subagent_service.run(
        user_goal=request.user_goal
    )

    return ApiResponse[dict](
        data=result
    )


@router.post(
    "/deepagents/subagents/run-parallel",
    response_model=ApiResponse[dict],
)
async def run_parallel_subagents(
    request: RunSubAgentFlowApiRequest,
) -> ApiResponse[dict]:
    result = deepagents_subagent_service.run_parallel_simulation(
        user_goal=request.user_goal
    )

    return ApiResponse[dict](
        data=result
    )


@router.get(
    "/deepagents/subagents/files",
    response_model=ApiResponse[list[str]],
)
async def list_files() -> ApiResponse[list[str]]:
    return ApiResponse[list[str]](
        data=deepagents_subagent_service.list_files()
    )


@router.get(
    "/deepagents/subagents/files/read",
    response_model=ApiResponse[dict],
)
async def read_file(
    file_path: str,
) -> ApiResponse[dict]:
    content = deepagents_subagent_service.read_file(
        file_path=file_path
    )

    return ApiResponse[dict](
        data={
            "file_path": file_path,
            "content": content,
        }
    )