from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.mcp_server_dev.service import mcp_server_dev_service
from app.schemas.response import ApiResponse


router = APIRouter()


class MCPServerToolCallApiRequest(BaseModel):
    tool_name: str = Field(..., min_length=1)
    arguments: dict = Field(default_factory=dict)
    role: str = Field(default="customer_service")
    user_id: str = Field(default="anonymous")
    tenant_id: str = Field(default="tenant_001")
    confirmed: bool = False


class MCPPromptRenderApiRequest(BaseModel):
    name: str = Field(..., min_length=1)
    arguments: dict = Field(default_factory=dict)


@router.get(
    "/mcp-server-dev/tools",
    response_model=ApiResponse[list[dict]],
)
async def list_tools(
    role: str = "customer_service",
) -> ApiResponse[list[dict]]:
    return ApiResponse[list[dict]](
        data=mcp_server_dev_service.list_tools(role)
    )


@router.post(
    "/mcp-server-dev/tools/call",
    response_model=ApiResponse[dict],
)
async def call_tool(
    request: MCPServerToolCallApiRequest,
) -> ApiResponse[dict]:
    return ApiResponse[dict](
        data=mcp_server_dev_service.call_tool(
            tool_name=request.tool_name,
            arguments=request.arguments,
            role=request.role,
            user_id=request.user_id,
            tenant_id=request.tenant_id,
            confirmed=request.confirmed,
        )
    )


@router.get(
    "/mcp-server-dev/resources",
    response_model=ApiResponse[list[dict]],
)
async def list_resources(
    role: str = "customer_service",
) -> ApiResponse[list[dict]]:
    return ApiResponse[list[dict]](
        data=mcp_server_dev_service.list_resources(role)
    )


@router.get(
    "/mcp-server-dev/resources/read",
    response_model=ApiResponse[dict],
)
async def read_resource(
    uri: str,
    role: str = "customer_service",
) -> ApiResponse[dict]:
    return ApiResponse[dict](
        data=mcp_server_dev_service.read_resource(
            uri=uri,
            role=role,
        )
    )


@router.get(
    "/mcp-server-dev/prompts",
    response_model=ApiResponse[list[dict]],
)
async def list_prompts() -> ApiResponse[list[dict]]:
    return ApiResponse[list[dict]](
        data=mcp_server_dev_service.list_prompts()
    )


@router.post(
    "/mcp-server-dev/prompts/render",
    response_model=ApiResponse[dict],
)
async def render_prompt(
    request: MCPPromptRenderApiRequest,
) -> ApiResponse[dict]:
    prompt = mcp_server_dev_service.render_prompt(
        name=request.name,
        arguments=request.arguments,
    )

    return ApiResponse[dict](
        data={
            "name": request.name,
            "prompt": prompt,
        }
    )


@router.get(
    "/mcp-server-dev/logs",
    response_model=ApiResponse[list[dict]],
)
async def list_logs() -> ApiResponse[list[dict]]:
    return ApiResponse[list[dict]](
        data=mcp_server_dev_service.list_logs()
    )