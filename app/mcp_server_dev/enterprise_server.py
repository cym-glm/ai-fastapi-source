from typing import Annotated

from pydantic import Field
from mcp.server import MCPServer

from app.mcp_server_dev.mock_systems import (
    MockCRMSystem,
    MockKnowledgeBaseSystem,
    MockOrderSystem,
)


mcp = MCPServer("Enterprise MCP Server")

order_system = MockOrderSystem()
crm_system = MockCRMSystem()
kb_system = MockKnowledgeBaseSystem()


@mcp.tool(title="查询订单状态")
def query_order_status(
    order_id: Annotated[str, Field(description="订单号，例如 10001")],
) -> dict:
    """根据订单号查询订单状态、金额、物流和是否可退款。"""
    return order_system.query_order_status(order_id)


@mcp.tool(title="搜索企业规则")
def search_enterprise_policy(
    query: Annotated[str, Field(description="用户问题或检索关键词")],
) -> list[dict]:
    """检索企业内部退款、物流、售后规则。"""
    return kb_system.search_policy(query)


@mcp.tool(title="查询客户信息")
def query_customer_profile(
    mobile: Annotated[str, Field(description="客户手机号")],
) -> dict:
    """根据手机号查询客户等级、标签和近期订单。"""
    return crm_system.query_customer(mobile)


@mcp.tool(title="发起订单退款")
def refund_order(
    order_id: Annotated[str, Field(description="订单号")],
    reason: Annotated[str, Field(description="退款原因")],
) -> dict:
    """
    为订单发起退款申请。

    注意：
    这是高风险写操作。
    生产环境必须接入权限校验、人工确认和审计日志。
    """
    return order_system.refund_order(
        order_id=order_id,
        reason=reason,
    )


@mcp.resource("policy://refund")
def refund_policy() -> str:
    """读取退款规则文档。"""
    return kb_system.read_policy("refund")


@mcp.resource("policy://logistics")
def logistics_policy() -> str:
    """读取物流规则文档。"""
    return kb_system.read_policy("logistics")


@mcp.resource("order://{order_id}")
def order_resource(order_id: str) -> str:
    """把订单信息作为 Resource 暴露。"""
    return str(
        order_system.query_order_status(order_id)
    )


@mcp.prompt(title="客服回复模板")
def customer_service_reply(
    question: Annotated[str, Field(description="用户问题")],
    context: Annotated[str, Field(description="参考资料")],
) -> str:
    """根据参考资料生成客服回复。"""
    return f"""
        你是电商客服助手。

        用户问题：
        {question}

        参考资料：
        {context}

        回答要求：
        1. 语气自然、口语化。
        2. 只能基于参考资料回答。
        3. 资料不足时说明“我这边暂时无法确认”。
        4. 涉及退款、赔付、修改订单等高风险动作时，不要直接承诺。
    """.strip()


@mcp.prompt(title="退款审核模板")
def refund_review_prompt(
    order_info: Annotated[str, Field(description="订单信息")],
    policy: Annotated[str, Field(description="退款规则")],
) -> str:
    """根据订单信息和退款规则生成退款审核判断。"""
    return f"""
请根据订单信息和退款规则判断是否可以退款。

订单信息：
{order_info}

退款规则：
{policy}

输出格式：
- 是否可退
- 判断依据
- 是否需要人工确认
- 给客服的建议话术
""".strip()