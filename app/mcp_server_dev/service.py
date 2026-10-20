from app.mcp_server_dev.local_registry import enterprise_mcp_registry


class MCPServerDevService:
    def list_tools(
        self,
        role: str = "customer_service",
    ) -> list[dict]:
        return enterprise_mcp_registry.list_tools(role)

    def call_tool(
        self,
        tool_name: str,
        arguments: dict,
        role: str = "customer_service",
        user_id: str = "anonymous",
        tenant_id: str = "tenant_001",
        confirmed: bool = False,
    ) -> dict:
        return enterprise_mcp_registry.call_tool(
            tool_name=tool_name,
            arguments=arguments,
            role=role,
            user_id=user_id,
            tenant_id=tenant_id,
            confirmed=confirmed,
        )

    def list_resources(
        self,
        role: str = "customer_service",
    ) -> list[dict]:
        return enterprise_mcp_registry.list_resources(role)

    def read_resource(
        self,
        uri: str,
        role: str = "customer_service",
    ) -> dict:
        return enterprise_mcp_registry.read_resource(
            uri=uri,
            role=role,
        )

    def list_prompts(self) -> list[dict]:
        return enterprise_mcp_registry.list_prompts()

    def render_prompt(
        self,
        name: str,
        arguments: dict,
    ) -> str:
        return enterprise_mcp_registry.render_prompt(
            name=name,
            arguments=arguments,
        )

    def list_logs(self) -> list[dict]:
        return enterprise_mcp_registry.list_logs()


mcp_server_dev_service = MCPServerDevService()