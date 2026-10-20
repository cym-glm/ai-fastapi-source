from app.mcp_intro.mcp_server import TeachingMCPServer
from app.mcp_intro.schemas import (
    MCPResource,
    MCPToolCall,
    MCPToolResult,
)


class TeachingMCPClient:
    """
    教学版 MCP Client。

    真实 MCP Client 会通过 stdio / HTTP 等 transport 和 server 通信。
    这里为了教学，直接持有 server 实例。
    """

    def __init__(
        self,
        server: TeachingMCPServer,
    ):
        self.server = server

    def initialize(self) -> dict:
        return self.server.manifest_as_dict()

    def list_tools(self) -> list[dict]:
        return self.server.list_tools()

    def call_tool(
        self,
        name: str,
        arguments: dict,
        confirmed: bool = False,
    ) -> MCPToolResult:
        return self.server.call_tool(
            MCPToolCall(
                name=name,
                arguments=arguments,
            ),
            confirmed=confirmed,
        )

    def list_resources(self) -> list[dict]:
        return self.server.list_resources()

    def read_resource(
        self,
        uri: str,
    ) -> MCPResource:
        return self.server.read_resource(uri)

    def list_prompts(self) -> list[dict]:
        return self.server.list_prompts()

    def get_prompt(
        self,
        name: str,
        arguments: dict,
    ) -> str:
        return self.server.get_prompt(
            name=name,
            arguments=arguments,
        )