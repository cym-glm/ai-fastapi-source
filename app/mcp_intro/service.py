from dataclasses import asdict

from app.mcp_intro.legacy_tools import (
    claude_tool_adapter_for_order,
    langchain_tool_adapter_for_order,
    openai_tool_adapter_for_order,
)
from app.mcp_intro.mcp_client import TeachingMCPClient
from app.mcp_intro.mcp_host import TeachingMCPHostAgent
from app.mcp_intro.mcp_server import TeachingMCPServer


class MCPIntroService:
    def __init__(self):
        self.server = TeachingMCPServer()
        self.client = TeachingMCPClient(self.server)
        self.host = TeachingMCPHostAgent(self.client)

    def show_without_mcp_problem(
        self,
        order_id: str = "10001",
    ) -> dict:
        return {
            "problem": "同一个订单查询能力，被不同平台重复包装。",
            "openai_adapter": openai_tool_adapter_for_order(order_id),
            "claude_adapter": claude_tool_adapter_for_order(
                {
                    "order_id": order_id,
                }
            ),
            "langchain_adapter": langchain_tool_adapter_for_order(order_id),
        }

    def get_manifest(self) -> dict:
        return self.server.manifest_as_dict()

    def list_tools(self) -> list[dict]:
        return self.client.list_tools()

    def call_tool(
        self,
        name: str,
        arguments: dict,
        confirmed: bool = False,
    ) -> dict:
        result = self.client.call_tool(
            name=name,
            arguments=arguments,
            confirmed=confirmed,
        )

        return asdict(result)

    def list_resources(self) -> list[dict]:
        return self.client.list_resources()

    def read_resource(
        self,
        uri: str,
    ) -> dict:
        return asdict(
            self.client.read_resource(uri)
        )

    def list_prompts(self) -> list[dict]:
        return self.client.list_prompts()

    def get_prompt(
        self,
        name: str,
        arguments: dict,
    ) -> str:
        return self.client.get_prompt(
            name=name,
            arguments=arguments,
        )

    def run_host_agent(
        self,
        user_request: str,
    ) -> dict:
        result = self.host.run(user_request)

        return asdict(result)


mcp_intro_service = MCPIntroService()