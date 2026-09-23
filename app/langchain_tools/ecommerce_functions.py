import uuid

from app.langchain_tools.schemas import (
    QueryOrderResult,
    QueryLogisticsResult,
    TransferHumanArgs,
    TransferHumanResult,
    QueryLogisticsArgs
)


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


MOCK_LOGISTICS = {
    "SF10001": {
        "tracking_no": "SF10001",
        "tracking_company": "顺丰",
        "latest_event": "包裹已到达成都高新区中转站。",
        "status": "in_transit",
    },
    "YT10003": {
        "tracking_no": "YT10003",
        "tracking_company": "圆通",
        "latest_event": "用户本人已签收。",
        "status": "delivered",
    },
}


async def query_order(order_id: str) -> QueryOrderResult:
    # 此处仅为示例，实际应用中应从数据库或其他存储系统中查询订单信息
    # 真实业务里面---查询真实的业务即可，接口：java -springboot  python -fastapi  node - nestjs go 
    order = MOCK_ORDERS.get(order_id)
    if not order:
        return QueryOrderResult(
            order_id=order_id,
            status="not_found",
            status_text="未查询到订单",
            tracking_company=None,
            tracking_no=None,
            latest_event=None,
        )

    return QueryOrderResult(**order)


async def query_logistics(tracking_no: str) -> QueryLogisticsResult:
    logistics = MOCK_LOGISTICS.get(tracking_no)

    if not logistics:
        return QueryLogisticsResult(
            tracking_no=tracking_no,
            tracking_company="未知",
            latest_event="未查询到物流信息",
            status="not_found",
        )

    return QueryLogisticsResult(**logistics)


async def transfer_human(reason: str) -> TransferHumanResult:
    ticket_id = f"ticket_{uuid.uuid4().hex[:8]}"

    return TransferHumanResult(
        ticket_id=ticket_id,
        message=f"已为您创建人工客服工单，原因：{reason}",
    )