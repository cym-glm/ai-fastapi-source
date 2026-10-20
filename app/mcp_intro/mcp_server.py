from dataclasses import asdict

from app.mcp_intro.legacy_tools import (
    LegacyCrmApi,
    LegacyKnowledgeBaseApi,
    LegacyOrderApi,
)
from app.mcp_intro.schemas import (
    MCPPrimitiveType,
    MCPPrompt,
    MCPResource,
    MCPServerInfo,
    MCPServerManifest,
    MCPTool,
    MCPToolCall,
    MCPToolResult,
)


class TeachingMCPServer:
    """
    教学版 MCP Server。

    目标：
    1. 统一暴露 tools。
    2. 统一暴露 resources。
    3. 统一暴露 prompts。
    4. 让不同 Host 可以通过同一种方式调用。
    """

    def __init__(self):
        self.order_api = LegacyOrderApi()
        self.kb_api = LegacyKnowledgeBaseApi()
        self.crm_api = LegacyCrmApi()

        self.server_info = MCPServerInfo(
            name="enterprise-demo-mcp-server",
            version="0.1.0",
            description="企业系统 MCP Server 教学版",
            capabilities=[
                MCPPrimitiveType.TOOL,
                MCPPrimitiveType.RESOURCE,
                MCPPrimitiveType.PROMPT,
            ],
        )

        self.tools = self._build_tools()
        self.resources = self._build_resources()
        self.prompts = self._build_prompts()

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "read_only": tool.read_only,
                "dangerous": tool.dangerous,
            }
            for tool in self.tools.values()
        ]

    def call_tool(
        self,
        tool_call: MCPToolCall,
        confirmed: bool = False,
    ) -> MCPToolResult:
        tool = self.tools.get(tool_call.name)

        if not tool:
            return MCPToolResult(
                name=tool_call.name,
                success=False,
                error_message=f"工具不存在：{tool_call.name}",
            )

        if tool.dangerous and not confirmed:
            return MCPToolResult(
                name=tool_call.name,
                success=False,
                error_message=f"高风险工具需要人工确认：{tool_call.name}",
            )

        try:
            result = tool.func(**tool_call.arguments)

            return MCPToolResult(
                name=tool_call.name,
                success=True,
                result=result,
            )
        except Exception as exc:
            return MCPToolResult(
                name=tool_call.name,
                success=False,
                error_message=str(exc),
            )

    def list_resources(self) -> list[dict]:
        return [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mime_type": resource.mime_type,
            }
            for resource in self.resources.values()
        ]

    def read_resource(
        self,
        uri: str,
    ) -> MCPResource:
        resource = self.resources.get(uri)

        if not resource:
            raise FileNotFoundError(
                f"资源不存在：{uri}"
            )

        return resource

    def list_prompts(self) -> list[dict]:
        return [
            {
                "name": prompt.name,
                "description": prompt.description,
                "arguments": prompt.arguments,
            }
            for prompt in self.prompts.values()
        ]

    def get_prompt(
        self,
        name: str,
        arguments: dict,
    ) -> str:
        prompt = self.prompts.get(name)

        if not prompt:
            raise ValueError(
                f"Prompt 不存在：{name}"
            )

        content = prompt.template

        for key, value in arguments.items():
            content = content.replace(
                "{{" + key + "}}",
                str(value),
            )

        return content

    def get_manifest(self) -> MCPServerManifest:
        return MCPServerManifest(
            server=self.server_info,
            tools=self.list_tools(),
            resources=self.list_resources(),
            prompts=self.list_prompts(),
        )

    def _build_tools(self) -> dict[str, MCPTool]:
        return {
            "query_order": MCPTool(
                name="query_order",
                description="根据订单号查询订单状态和物流信息。",
                input_schema={
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "订单号",
                        }
                    },
                    "required": ["order_id"],
                },
                func=self._query_order,
                read_only=True,
                dangerous=False,
            ),
            "search_knowledge_base": MCPTool(
                name="search_knowledge_base",
                description="检索企业知识库，适合查询退款、物流、售后、内部规则。",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "检索关键词或问题",
                        }
                    },
                    "required": ["query"],
                },
                func=self._search_kb,
                read_only=True,
                dangerous=False,
            ),
            "query_customer": MCPTool(
                name="query_customer",
                description="根据手机号查询客户等级和标签。",
                input_schema={
                    "type": "object",
                    "properties": {
                        "mobile": {
                            "type": "string",
                            "description": "客户手机号",
                        }
                    },
                    "required": ["mobile"],
                },
                func=self._query_customer,
                read_only=True,
                dangerous=False,
            ),
            "refund_order": MCPTool(
                name="refund_order",
                description="为订单发起退款。高风险写操作，必须人工确认。",
                input_schema={
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "订单号",
                        },
                        "reason": {
                            "type": "string",
                            "description": "退款原因",
                        },
                    },
                    "required": ["order_id", "reason"],
                },
                func=self._refund_order,
                read_only=False,
                dangerous=True,
            ),
        }

    def _build_resources(self) -> dict[str, MCPResource]:
        return {
            "kb://refund-policy": MCPResource(
                uri="kb://refund-policy",
                name="退款规则文档",
                description="企业内部退款规则。",
                mime_type="text/markdown",
                content=(
                    "# 退款规则\n\n"
                    "订单未发货可以申请退款；"
                    "订单已发货需要用户收到货后走售后流程。"
                ),
            ),
            "kb://logistics-policy": MCPResource(
                uri="kb://logistics-policy",
                name="物流规则文档",
                description="企业内部物流异常处理规则。",
                mime_type="text/markdown",
                content=(
                    "# 物流规则\n\n"
                    "物流超过 7 天未更新，可以联系人工客服进行排查。"
                ),
            ),
        }

    def _build_prompts(self) -> dict[str, MCPPrompt]:
        return {
            "customer_service_reply": MCPPrompt(
                name="customer_service_reply",
                description="电商客服回复模板。",
                arguments=["question", "context"],
                template=(
                    "你是电商客服助手。\n"
                    "用户问题：{{question}}\n"
                    "参考资料：{{context}}\n"
                    "请用口语化方式回答，不能编造。"
                ),
            ),
            "refund_review": MCPPrompt(
                name="refund_review",
                description="退款审核 Prompt 模板。",
                arguments=["order_info", "policy"],
                template=(
                    "请根据订单信息和退款规则判断是否可以退款。\n"
                    "订单信息：{{order_info}}\n"
                    "退款规则：{{policy}}\n"
                    "输出：是否可退、原因、是否需要人工确认。"
                ),
            ),
        }

    def _query_order(
        self,
        order_id: str,
    ) -> dict:
        return self.order_api.get_order(order_id)

    def _search_kb(
        self,
        query: str,
    ) -> list[dict]:
        return self.kb_api.search_docs(query)

    def _query_customer(
        self,
        mobile: str,
    ) -> dict:
        return self.crm_api.get_customer(mobile)

    def _refund_order(
        self,
        order_id: str,
        reason: str,
    ) -> dict:
        return {
            "order_id": order_id,
            "status": "refund_requested",
            "reason": reason,
            "message": "已模拟发起退款申请。",
        }

    def manifest_as_dict(self) -> dict:
        return asdict(self.get_manifest())