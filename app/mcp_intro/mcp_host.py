from app.mcp_intro.mcp_client import TeachingMCPClient
from app.mcp_intro.schemas import MCPHostRunResult


class TeachingMCPHostAgent:
    """
    教学版 Host Agent。

    Host 负责：
    1. 接收用户请求。
    2. 通过 MCP Client 发现工具。
    3. 选择合适工具。
    4. 调用 MCP Server。
    5. 整合最终回答。
    """

    def __init__(
        self,
        client: TeachingMCPClient,
    ):
        self.client = client

    def run(
        self,
        user_request: str,
    ) -> MCPHostRunResult:
        trace: list[str] = []

        manifest = self.client.initialize()
        trace.append(
            f"连接 MCP Server：{manifest['server']['name']}"
        )

        tools = self.client.list_tools()
        trace.append(
            f"发现工具数量：{len(tools)}"
        )

        selected_tool = self._select_tool(user_request)
        trace.append(
            f"选择工具：{selected_tool}"
        )

        if not selected_tool:
            return MCPHostRunResult(
                user_request=user_request,
                selected_tool=None,
                tool_result=None,
                final_answer="当前请求不需要调用 MCP 工具。",
                trace=trace,
            )

        tool_result = self._call_selected_tool(
            selected_tool,
            user_request,
        )

        trace.append(
            f"工具调用结果：success={tool_result.success}"
        )

        final_answer = self._build_answer(
            user_request=user_request,
            selected_tool=selected_tool,
            tool_result=tool_result,
        )

        return MCPHostRunResult(
            user_request=user_request,
            selected_tool=selected_tool,
            tool_result=tool_result,
            final_answer=final_answer,
            trace=trace,
        )

    def _select_tool(
        self,
        user_request: str,
    ) -> str | None:
        if "订单" in user_request:
            return "query_order"

        if any(word in user_request for word in ["退款", "物流", "售后", "规则"]):
            return "search_knowledge_base"

        if any(word in user_request for word in ["客户", "手机号", "会员"]):
            return "query_customer"

        return None

    def _call_selected_tool(
        self,
        selected_tool: str,
        user_request: str,
    ):
        if selected_tool == "query_order":
            order_id = self._extract_order_id(user_request)

            return self.client.call_tool(
                name="query_order",
                arguments={
                    "order_id": order_id,
                },
            )

        if selected_tool == "search_knowledge_base":
            return self.client.call_tool(
                name="search_knowledge_base",
                arguments={
                    "query": user_request,
                },
            )

        if selected_tool == "query_customer":
            return self.client.call_tool(
                name="query_customer",
                arguments={
                    "mobile": "13800000000",
                },
            )

        return self.client.call_tool(
            name=selected_tool,
            arguments={},
        )

    def _extract_order_id(
        self,
        text: str,
    ) -> str:
        digits = "".join(
            char for char in text
            if char.isdigit()
        )

        return digits or "10001"

    def _build_answer(
        self,
        user_request: str,
        selected_tool: str,
        tool_result,
    ) -> str:
        if not tool_result.success:
            return (
                f"我尝试通过 MCP 工具 {selected_tool} 处理你的问题，"
                f"但调用失败：{tool_result.error_message}"
            )

        return (
            f"我已经通过 MCP 工具 `{selected_tool}` 查询到结果。\n\n"
            f"用户问题：{user_request}\n\n"
            f"工具结果：{tool_result.result}\n\n"
            "这个过程体现了 MCP 的价值：Host 不直接耦合企业系统，"
            "而是通过 MCP Client 调用 MCP Server 暴露的标准工具。"
        )