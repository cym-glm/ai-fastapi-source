from dataclasses import asdict

from app.mcp_server_dev.mock_systems import (
    MockCRMSystem,
    MockKnowledgeBaseSystem,
    MockOrderSystem,
)
from app.mcp_server_dev.schemas import (
    EnterprisePromptMeta,
    EnterpriseResourceMeta,
    EnterpriseToolCallLog,
    EnterpriseToolMeta,
    MCPToolRiskLevel,
)


class EnterpriseMCPLocalRegistry:
    """
    教学版本地 MCP Registry。

    说明：
    真实 MCP Server 通过 MCP 协议暴露能力。
    这个 Registry 是为了让 FastAPI 和脚本可以本地测试同样的业务能力。
    """

    def __init__(self):
        self.order_system = MockOrderSystem()
        self.crm_system = MockCRMSystem()
        self.kb_system = MockKnowledgeBaseSystem()
        self.logs: list[EnterpriseToolCallLog] = []

        self.tools = {
            "query_order_status": EnterpriseToolMeta(
                name="query_order_status",
                description="根据订单号查询订单状态、金额、物流和是否可退款。",
                risk_level=MCPToolRiskLevel.LOW,
                read_only=True,
                required_roles=["customer_service", "admin"],
            ),
            "search_enterprise_policy": EnterpriseToolMeta(
                name="search_enterprise_policy",
                description="检索企业内部退款、物流、售后规则。",
                risk_level=MCPToolRiskLevel.LOW,
                read_only=True,
                required_roles=["customer_service", "admin"],
            ),
            "query_customer_profile": EnterpriseToolMeta(
                name="query_customer_profile",
                description="根据手机号查询客户等级、标签和近期订单。",
                risk_level=MCPToolRiskLevel.MEDIUM,
                read_only=True,
                required_roles=["customer_service", "admin"],
            ),
            "refund_order": EnterpriseToolMeta(
                name="refund_order",
                description="为订单发起退款申请。",
                risk_level=MCPToolRiskLevel.HIGH,
                read_only=False,
                required_roles=["admin"],
            ),
        }

        self.resources = {
            "policy://refund": EnterpriseResourceMeta(
                uri="policy://refund",
                title="退款规则",
                description="企业内部退款规则文档。",
                required_roles=["customer_service", "admin"],
            ),
            "policy://logistics": EnterpriseResourceMeta(
                uri="policy://logistics",
                title="物流规则",
                description="企业内部物流规则文档。",
                required_roles=["customer_service", "admin"],
            ),
        }

        self.prompts = {
            "customer_service_reply": EnterprisePromptMeta(
                name="customer_service_reply",
                title="客服回复模板",
                description="根据问题和参考资料生成客服回复。",
                arguments=["question", "context"],
            ),
            "refund_review_prompt": EnterprisePromptMeta(
                name="refund_review_prompt",
                title="退款审核模板",
                description="根据订单信息和退款规则做退款审核。",
                arguments=["order_info", "policy"],
            ),
        }

    def list_tools(
        self,
        role: str,
    ) -> list[dict]:
        return [
            asdict(meta)
            for meta in self.tools.values()
            if role in meta.required_roles
        ]

    def call_tool(
        self,
        tool_name: str,
        arguments: dict,
        role: str,
        user_id: str = "anonymous",
        tenant_id: str = "tenant_001",
        confirmed: bool = False,
    ) -> dict:
        meta = self.tools.get(tool_name)

        if not meta:
            return self._log_and_return(
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                error_message=f"工具不存在：{tool_name}",
                user_id=user_id,
                tenant_id=tenant_id,
                confirmed=confirmed,
            )

        if role not in meta.required_roles:
            return self._log_and_return(
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                error_message=f"角色 {role} 无权调用工具 {tool_name}",
                user_id=user_id,
                tenant_id=tenant_id,
                confirmed=confirmed,
            )

        if meta.risk_level == MCPToolRiskLevel.HIGH and not confirmed:
            return self._log_and_return(
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                error_message=f"高风险工具 {tool_name} 需要人工确认。",
                user_id=user_id,
                tenant_id=tenant_id,
                confirmed=confirmed,
            )

        try:
            result = self._execute_tool(tool_name, arguments)

            return self._log_and_return(
                tool_name=tool_name,
                arguments=arguments,
                success=True,
                result=result,
                user_id=user_id,
                tenant_id=tenant_id,
                confirmed=confirmed,
            )
        except Exception as exc:
            return self._log_and_return(
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                error_message=str(exc),
                user_id=user_id,
                tenant_id=tenant_id,
                confirmed=confirmed,
            )

    def list_resources(
        self,
        role: str,
    ) -> list[dict]:
        return [
            asdict(meta)
            for meta in self.resources.values()
            if role in meta.required_roles
        ]

    def read_resource(
        self,
        uri: str,
        role: str,
    ) -> dict:
        meta = self.resources.get(uri)

        if not meta:
            raise FileNotFoundError(
                f"资源不存在：{uri}"
            )

        if role not in meta.required_roles:
            raise PermissionError(
                f"角色 {role} 无权读取资源 {uri}"
            )

        if uri == "policy://refund":
            content = self.kb_system.read_policy("refund")
        elif uri == "policy://logistics":
            content = self.kb_system.read_policy("logistics")
        else:
            content = ""

        return {
            **asdict(meta),
            "content": content,
        }

    def list_prompts(self) -> list[dict]:
        return [
            asdict(meta)
            for meta in self.prompts.values()
        ]

    def render_prompt(
        self,
        name: str,
        arguments: dict,
    ) -> str:
        if name == "customer_service_reply":
            return f"""
你是电商客服助手。

用户问题：
{arguments.get("question", "")}

参考资料：
{arguments.get("context", "")}

请用自然、口语化方式回答。
资料不足时说明“我这边暂时无法确认”。
""".strip()

        if name == "refund_review_prompt":
            return f"""
请根据订单信息和退款规则判断是否可以退款。

订单信息：
{arguments.get("order_info", "")}

退款规则：
{arguments.get("policy", "")}

输出：
1. 是否可退
2. 判断依据
3. 是否需要人工确认
4. 客服回复建议
""".strip()

        raise ValueError(
            f"Prompt 不存在：{name}"
        )

    def list_logs(self) -> list[dict]:
        return [
            asdict(log)
            for log in self.logs
        ]

    def _execute_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):
        if tool_name == "query_order_status":
            return self.order_system.query_order_status(
                arguments["order_id"]
            )

        if tool_name == "search_enterprise_policy":
            return self.kb_system.search_policy(
                arguments["query"]
            )

        if tool_name == "query_customer_profile":
            return self.crm_system.query_customer(
                arguments["mobile"]
            )

        if tool_name == "refund_order":
            return self.order_system.refund_order(
                order_id=arguments["order_id"],
                reason=arguments["reason"],
            )

        raise ValueError(
            f"未实现工具：{tool_name}"
        )

    def _log_and_return(
        self,
        tool_name: str,
        arguments: dict,
        success: bool,
        result=None,
        error_message: str | None = None,
        user_id: str = "anonymous",
        tenant_id: str = "tenant_001",
        confirmed: bool = False,
    ) -> dict:
        log = EnterpriseToolCallLog(
            tool_name=tool_name,
            arguments=arguments,
            success=success,
            result=result,
            error_message=error_message,
            user_id=user_id,
            tenant_id=tenant_id,
            confirmed=confirmed,
        )

        self.logs.append(log)

        return asdict(log)


enterprise_mcp_registry = EnterpriseMCPLocalRegistry()