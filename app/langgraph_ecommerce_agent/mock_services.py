import asyncio


MOCK_ORDERS = {
    "10001": {
        "order_id": "10001",
        "status": "shipped",
        "status_text": "已发货",
        "amount": 399.0,
        "currency": "CNY",
        "tracking_company": "顺丰",
        "tracking_no": "SF10001",
        "latest_event": "包裹已到达成都高新区中转站。",
    },
    "10002": {
        "order_id": "10002",
        "status": "paid",
        "status_text": "已付款，待发货",
        "amount": 199.0,
        "currency": "CNY",
        "tracking_company": None,
        "tracking_no": None,
        "latest_event": None,
    },
    "10003": {
        "order_id": "10003",
        "status": "paid",
        "status_text": "已付款，待发货",
        "amount": 1299.0,
        "currency": "CNY",
        "tracking_company": None,
        "tracking_no": None,
        "latest_event": None,
    },
}


def extract_order_id_from_text(text: str) -> str | None:
    for order_id in MOCK_ORDERS:
        if order_id in text:
            return order_id

    if "99999" in text:
        return "99999"

    return None


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
                "amount": 0.0,
                "currency": "CNY",
                "tracking_company": None,
                "tracking_no": None,
                "latest_event": None,
            },
        }

    return {
        "success": True,
        "error": None,
        "data": order,
    }


async def mock_query_logistics(order_info: dict | None) -> dict:
    await asyncio.sleep(0.05)

    if not order_info:
        return {
            "success": False,
            "message": "缺少订单信息",
            "data": None,
        }

    if not order_info.get("tracking_no"):
        return {
            "success": False,
            "message": "当前订单暂无物流单号",
            "data": None,
        }

    return {
        "success": True,
        "message": "物流查询成功",
        "data": {
            "tracking_company": order_info.get("tracking_company"),
            "tracking_no": order_info.get("tracking_no"),
            "latest_event": order_info.get("latest_event"),
        },
    }


async def mock_retrieve_policy(query: str | None) -> dict:
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
            "answer": "根据售后规则，订单未发货时，用户可以申请取消订单并退款。",
            "sources": [
                {
                    "document_id": "ecommerce_after_sales",
                    "chunk_id": "refund_paid_order",
                    "source": "data/knowledge_base/ecommerce_after_sales.md",
                    "content_preview": "订单未发货时，用户可以申请取消订单并退款。",
                    "score": 0.93,
                }
            ],
        }

    if "已发货" in query or "已签收" in query:
        return {
            "hit": True,
            "answer": "根据售后规则，订单已发货后，需要用户收到商品后再发起退货退款申请。",
            "sources": [
                {
                    "document_id": "ecommerce_after_sales",
                    "chunk_id": "refund_shipped_order",
                    "source": "data/knowledge_base/ecommerce_after_sales.md",
                    "content_preview": "订单已发货后，需要用户收到商品后再发起退货退款申请。",
                    "score": 0.9,
                }
            ],
        }

    if "售后" in query:
        return {
            "hit": True,
            "answer": "售后问题需要结合订单状态、商品状态和平台规则综合判断。",
            "sources": [
                {
                    "document_id": "ecommerce_after_sales",
                    "chunk_id": "after_sales_general",
                    "source": "data/knowledge_base/ecommerce_after_sales.md",
                    "content_preview": "售后问题需要结合订单状态、商品状态和平台规则综合判断。",
                    "score": 0.82,
                }
            ],
        }

    return {
        "hit": False,
        "answer": "根据当前知识库无法确认。",
        "sources": [],
    }


async def mock_execute_refund(payload: dict) -> dict:
    await asyncio.sleep(0.05)

    return {
        "success": True,
        "refund_id": f"rf_{payload.get('order_id', 'unknown')}",
        "executed_payload": payload,
    }


async def mock_transfer_human(reason: str) -> dict:
    await asyncio.sleep(0.05)

    return {
        "success": True,
        "ticket_id": "ticket_10001",
        "reason": reason,
    }