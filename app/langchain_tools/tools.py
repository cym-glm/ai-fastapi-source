import json

from langchain_core.tools import tool, StructuredTool


from app.langchain_tools.ecommerce_functions import (
    query_logistics,
    query_order,
    transfer_human
)

from app.langchain_tools.schemas import (
    QueryLogisticsArgs,
    QueryOrderArgs,
    TransferHumanArgs,
    QueryOrderResult,
    TransferHumanResult
)


@tool
async def query_order_simple(order_id: str) -> str:
    """根据订单号查询订单状态和物流信息。当用户询问订单状态、发货状态、物流状态时使用。"""
    result = await query_order(order_id)
    return json.dumps(result.model_dump(), ensure_ascii=False)


@tool
async def query_logistics_simple(tracking_no: str) -> str:
    """根据物流单号查询物流信息。当用户询问快递状态、物流跟踪时使用。"""
    result = await query_logistics(tracking_no)
    return json.dumps(result.model_dump(), ensure_ascii=False)


@tool
async def transfer_human_simple(reason: str) -> str:
    """将当前对话转接给人工客服，并提供转接原因。当无法处理用户的请求或需要人工介入时使用。"""
    result = await transfer_human(reason)
    json.dumps(result.model_dump(), ensure_ascii=False)
    # return json.dumps(
    #     {
    #         "ticket_id": result.ticket_id,
    #         "status": "created",
    #         "message": result.message,
    #     },
    #     ensure_ascii=False,
    # )



query_order_tool = StructuredTool.from_function(
    coroutine=query_order,
    name="query_order",
    description="根据订单号查询订单状态和物流信息。当用户询问订单状态、发货状态、物流状态时使用。",
    args_schema=QueryOrderArgs
)

query_logistics_tool = StructuredTool.from_function(
    coroutine=query_logistics,
    name="query_logistics",
    description= "根据物流单号查询物流信息。当用户询问快递状态、物流跟踪时使用。",
    args_schema=QueryLogisticsArgs
)

transfer_human_tool = StructuredTool.from_function(
    coroutine=transfer_human,
    name="transfer_human",
    description= "将当前对话转接给人工客服，并提供转接原因。当无法处理用户的请求或需要人工介入时使用。",
    args_schema=TransferHumanArgs
)

# 电商客服对话助手
ECOMMERCE_LANGCHAIN_TOOLS = [
    query_order_tool,
    query_logistics_tool,
    transfer_human_tool
]