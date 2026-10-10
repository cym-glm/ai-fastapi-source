def mock_query_order(order_id: str | None) -> dict:
    orders = {
        "10001": {
            "order_id": "10001",
            "status": "shipped",
            "status_text": "已发货",
        },
        "10002": {
            "order_id": "10002",
            "status": "paid",
            "status_text": "已付款，待发货",
        },
    }

    if not order_id:
        return {
            "success": False,
            "message": "缺少订单号",
            "data": None,
        }

    order = orders.get(order_id)

    if not order:
        return {
            "success": False,
            "message": "未查询到订单",
            "data": None,
        }

    return {
        "success": True,
        "message": "订单查询成功",
        "data": order,
    }


def mock_refund_policy(order_status: str | None) -> str:
    if order_status == "paid":
        return "订单未发货时，可以申请取消订单并退款。"

    if order_status == "shipped":
        return "订单已发货后，需要用户收到商品后再申请退货退款。"

    return "当前订单状态无法确认退款规则，建议转人工。"


def mock_query_sales_data() -> dict:
    return {
        "period": "最近 30 天",
        "total_orders": 1200,
        "total_amount": 368000,
        "last_period_orders": 1500,
        "last_period_amount": 450000,
        "top_category": "AI 课程",
        "weak_category": "传统前端课程",
    }


def extract_order_id(question: str) -> str | None:
    if "10001" in question:
        return "10001"

    if "10002" in question:
        return "10002"

    return None