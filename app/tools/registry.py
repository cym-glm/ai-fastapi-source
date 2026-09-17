from app.tools.base import ToolDefinition
from app.tools.ecommerce import (
    query_logistics,
    query_order,
    transfer_human,
)
from app.tools.schemas import (
    QueryLogisticsArgs,
    QueryLogisticsResult,
    QueryOrderArgs,
    QueryOrderResult,
    TransferHumanArgs,
    TransferHumanResult,
)


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition):
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise KeyError(f"工具不存在：{name}")

        tool = self._tools[name]

        if not tool.enabled:
            raise KeyError(f"工具已禁用：{name}")

        return tool

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def to_openai_tools(self) -> list[dict]:
        return [
            tool.to_openai_tool()
            for tool in self._tools.values()
            if tool.enabled
        ]


tool_registry = ToolRegistry()

tool_registry.register(
    ToolDefinition(
        name="query_order",
        description="根据订单号查询订单状态和物流信息。当用户询问订单状态、发货状态、物流状态时使用。",
        args_schema=QueryOrderArgs,
        result_schema=QueryOrderResult,
        func=query_order,
    )
)

tool_registry.register(
    ToolDefinition(
        name="query_logistics",
        description="根据物流单号查询物流轨迹。当用户已经提供物流单号，并询问包裹运输状态时使用。",
        args_schema=QueryLogisticsArgs,
        result_schema=QueryLogisticsResult,
        func=query_logistics,
    )
)

tool_registry.register(
    ToolDefinition(
        name="transfer_human",
        description="当用户明确要求人工客服，或者问题超出 AI 能力范围时创建人工客服工单。",
        args_schema=TransferHumanArgs,
        result_schema=TransferHumanResult,
        func=transfer_human,
    )
)