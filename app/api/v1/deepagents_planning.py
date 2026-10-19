from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.deepagents_planning.service import deepagents_planning_service
from app.schemas.response import ApiResponse


router = APIRouter()


class CreatePlanApiRequest(BaseModel):
    user_goal: str = Field(..., min_length=1)


class RunPlanningApiRequest(BaseModel):
    user_goal: str = Field(..., min_length=1)
    allow_replan: bool = True


@router.post(
    "/deepagents/planning/plan",
    response_model=ApiResponse[dict],
)
async def create_plan(
    request: CreatePlanApiRequest,
) -> ApiResponse[dict]:
    plan = deepagents_planning_service.create_plan(
        request.user_goal
    )

    return ApiResponse[dict](
        data=plan
    )


@router.post(
    "/deepagents/planning/run",
    response_model=ApiResponse[dict],
)
async def run_planning(
    request: RunPlanningApiRequest,
) -> ApiResponse[dict]:
    result = deepagents_planning_service.run_goal(
        user_goal=request.user_goal,
        allow_replan=request.allow_replan,
    )

    return ApiResponse[dict](
        data=result
    )


@router.get(
    "/deepagents/planning/files",
    response_model=ApiResponse[list[str]],
)
async def list_files() -> ApiResponse[list[str]]:
    return ApiResponse[list[str]](
        data=deepagents_planning_service.list_files()
    )


@router.get(
    "/deepagents/planning/files/read",
    response_model=ApiResponse[dict],
)
async def read_file(
    file_path: str,
) -> ApiResponse[dict]:
    content = deepagents_planning_service.read_file(
        file_path
    )

    return ApiResponse[dict](
        data={
            "file_path": file_path,
            "content": content,
        }
    )