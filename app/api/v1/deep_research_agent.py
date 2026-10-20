from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.deep_research_agent.schemas import DeepResearchRequest
from app.deep_research_agent.service import deep_research_agent_service
from app.schemas.response import ApiResponse


router = APIRouter()


class DeepResearchApiRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    objective: str = Field(default="输出一份结构化研究报告")
    tenant_id: str = Field(default="tenant_001")
    user_id: str = Field(default="anonymous")
    max_sources: int = Field(default=6, ge=1, le=20)
    include_enterprise_kb: bool = True
    include_web: bool = True


@router.post(
    "/deep-research/run",
    response_model=ApiResponse[dict],
)
async def run_deep_research(
    request: DeepResearchApiRequest,
) -> ApiResponse[dict]:
    result = deep_research_agent_service.run(
        DeepResearchRequest(
            topic=request.topic,
            objective=request.objective,
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            max_sources=request.max_sources,
            include_enterprise_kb=request.include_enterprise_kb,
            include_web=request.include_web,
        )
    )

    return ApiResponse[dict](
        data=asdict(result)
    )


@router.get(
    "/deep-research/files",
    response_model=ApiResponse[list[str]],
)
async def list_files() -> ApiResponse[list[str]]:
    return ApiResponse[list[str]](
        data=deep_research_agent_service.list_files()
    )


@router.get(
    "/deep-research/files/read",
    response_model=ApiResponse[dict],
)
async def read_file(
    file_path: str,
) -> ApiResponse[dict]:
    content = deep_research_agent_service.read_file(
        file_path=file_path
    )

    return ApiResponse[dict](
        data={
            "file_path": file_path,
            "content": content,
        }
    )


@router.post(
    "/deep-research/clear",
    response_model=ApiResponse[dict],
)
async def clear_workspace() -> ApiResponse[dict]:
    deep_research_agent_service.clear_workspace()

    return ApiResponse[dict](
        data={
            "message": "workspace cleared"
        }
    )


@router.get(
    "/deep-research/health",
    response_model=ApiResponse[dict],
)
async def health() -> ApiResponse[dict]:
    return ApiResponse[dict](
        data={
            "status": "ok",
            "service": "Deep Research Agent"
        }
    )