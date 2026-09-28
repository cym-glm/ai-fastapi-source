import asyncio

from app.langgraph_routing.schemas import RoutingState


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
    "10003": {
        "order_id": "10003",
        "status": "delivered",
        "status_text": "已签收",
        "tracking_company": "圆通",
        "tracking_no": "YT10003",
        "latest_event": "用户本人已签收。",
    },
}


async def mock_query_order(order_id: str | None) -> dict:
    await asyncio.sleep(0.05)

    if not order_id:
        return {
            "success": False,
            "error": "missing_order_id",
            "data": None,
        }

    order = MOCK_ORDERS.get(order_id)

    if not order:
        return {
            "success": False,
            "error": "order_not_found",
            "data": {
                "order_id": order_id,
                "status": "not_found",
                "status_text": "未查询到订单",
            },
        }

    return {
        "success": True,
        "error": None,
        "data": order,
    }


async def mock_search_policy(query: str | None) -> dict:
    await asyncio.sleep(0.05)

    if not query:
        return {
            "hit": False,
            "answer": "根据当前知识库无法确认。",
            "sources": [],
        }

    if "未发货" in query or "待发货" in query:
        return {
            "hit": True,
            "answer": "订单未发货时，用户可以申请取消订单并退款。",
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

    if "已发货" in query or "已签收" in query:
        return {
            "hit": True,
            "answer": "订单已发货后，需要用户收到商品后再发起退货退款申请。",
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
        "hit": False,
        "answer": "根据当前知识库无法确认。",
        "sources": [],
    }



def create_initial_state(
    user_question: str,
) -> RoutingState:
    return {
        "user_question": user_question,

        "intent": "unknown",

        "order_id": None,
        "order_info": None,

        "need_policy": False,
        "policy_query": None,
        "policy_answer": None,
        "sources": [],

        "tool_success": True,
        "tool_calls": [],

        "rag_hit": False,
        "need_human_confirm": False,
        "risk_level": "low",
        "pending_action": None,

        "retry_count": 0,
        "max_retry": 2,

        "final_answer": "",
        "is_finished": False,

        "logs": [],
        "errors": [],
    }