import asyncio


MOCK_ORDERS = {
    "10001": {
        "order_id": "10001",
        "status": "shipped",
        "status_text": "已发货",
        "tracking_company": "顺丰",
        "tracking_no": "SF10001",
        "latest_event": "包裹已到达成都高新区中转站。",
    },
    "10002": {
        "order_id": "10002",
        "status": "paid",
        "status_text": "已付款，待发货",
        "tracking_company": None,
        "tracking_no": None,
        "latest_event": None,
    },
}


async def mock_query_order(order_id: str | None) -> dict:
    await asyncio.sleep(0.05)

    if not order_id:
        return {
            "order_id": "",
            "status": "missing_order_id",
            "status_text": "缺少订单号",
            "tracking_company": None,
            "tracking_no": None,
            "latest_event": None,
        }

    return MOCK_ORDERS.get(
        order_id,
        {
            "order_id": order_id,
            "status": "not_found",
            "status_text": "未查询到订单",
            "tracking_company": None,
            "tracking_no": None,
            "latest_event": None,
        },
    )


async def mock_retrieve_policy(
    order_status: str | None,
) -> dict:
    await asyncio.sleep(0.05)

    if order_status == "paid":
        return {
            "policy_query": "订单未发货退款规则",
            "policy_answer": "订单未发货时，用户可以申请取消订单并退款。",
            "sources": [
                {
                    "document_id": "ecommerce_after_sales",
                    "chunk_id": "ecommerce_after_sales_chunk_0",
                    "source": "data/knowledge_base/ecommerce_after_sales.md",
                    "content_preview": "订单未发货时，用户可以申请取消订单并退款。",
                    "score": 0.92,
                }
            ],
        }

    if order_status == "shipped":
        return {
            "policy_query": "订单已发货退货退款规则",
            "policy_answer": "订单已发货后，需要用户收到商品后再发起退货退款申请。",
            "sources": [
                {
                    "document_id": "ecommerce_after_sales",
                    "chunk_id": "ecommerce_after_sales_chunk_1",
                    "source": "data/knowledge_base/ecommerce_after_sales.md",
                    "content_preview": "订单已发货后，需要用户收到商品后再发起退货退款申请。",
                    "score": 0.89,
                }
            ],
        }

    return {
        "policy_query": "退款规则",
        "policy_answer": "当前订单状态无法确认退款规则，建议转人工客服。",
        "sources": [],
    }


def create_initial_state(
    user_question: str,
) -> dict:
    return {
        "user_question": user_question,

        "intent": "unknown",

        "order_id": None,
        "order_info": None,

        "policy_query": None,
        "policy_answer": None,
        "sources": [],

        "need_human_confirm": False,
        "risk_level": "low",
        "pending_action": None,

        "tool_calls": [],
        "logs": [],
        "errors": [],

        "final_answer": "",
        "retry_count": 0,
        "is_finished": False,
    }