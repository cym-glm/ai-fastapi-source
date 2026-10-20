from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.mcp_intro.service import mcp_intro_service
from app.schemas.response import ApiResponse


router = APIRouter()


class MCPToolCallApiRequest(BaseModel):
    name: str = Field(..., min_length=1)
    arguments: dict = Field(default_factory=dict)
    confirmed: bool = False


class MCPHostRunApiRequest(BaseModel):
    user_request: str = Field(..., min_length=1)


@router.get(
    "/mcp-intro/without-mcp",
    response_model=ApiResponse[dict],
)
async def without_mcp(
    order_id: str = "10001",
) -> ApiResponse[dict]:
    return ApiResponse[dict](
        data=mcp_intro_service.show_without_mcp_problem(
            order_id=order_id
        )
    )


@router.get(
    "/mcp-intro/manifest",
    response_model=ApiResponse[dict],
)
async def manifest() -> ApiResponse[dict]:
    return ApiResponse[dict](
        data=mcp_intro_service.get_manifest()
    )


@router.get(
    "/mcp-intro/tools",
    response_model=ApiResponse[list[dict]],
)
async def list_tools() -> ApiResponse[list[dict]]:
    return ApiResponse[list[dict]](
        data=mcp_intro_service.list_tools()
    )


@router.post(
    "/mcp-intro/tools/call",
    response_model=ApiResponse[dict],
)
async def call_tool(
    request: MCPToolCallApiRequest,
) -> ApiResponse[dict]:
    result = mcp_intro_service.call_tool(
        name=request.name,
        arguments=request.arguments,
        confirmed=request.confirmed,
    )

    return ApiResponse[dict](
        data=result
    )


@router.get(
    "/mcp-intro/resources",
    response_model=ApiResponse[list[dict]],
)
async def list_resources() -> ApiResponse[list[dict]]:
    return ApiResponse[list[dict]](
        data=mcp_intro_service.list_resources()
    )


@router.get(
    "/mcp-intro/resources/read",
    response_model=ApiResponse[dict],
)
async def read_resource(
    uri: str,
) -> ApiResponse[dict]:
    return ApiResponse[dict](
        data=mcp_intro_service.read_resource(uri)
    )


@router.post(
    "/mcp-intro/host/run",
    response_model=ApiResponse[dict],
)
async def run_host(
    request: MCPHostRunApiRequest,
) -> ApiResponse[dict]:
    return ApiResponse[dict](
        data=mcp_intro_service.run_host_agent(
            request.user_request
        )
    )