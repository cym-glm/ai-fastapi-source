from app.mcp_intro.service import mcp_intro_service


def main():
    print("调用 query_order:")
    result = mcp_intro_service.call_tool(
        name="query_order",
        arguments={
            "order_id": "10001",
        },
    )
    print(result)

    print("=" * 80)
    print("调用 refund_order，不确认:")
    result = mcp_intro_service.call_tool(
        name="refund_order",
        arguments={
            "order_id": "10001",
            "reason": "用户取消订单",
        },
        confirmed=False,
    )
    print(result)

    print("=" * 80)
    print("调用 refund_order，已确认:")
    result = mcp_intro_service.call_tool(
        name="refund_order",
        arguments={
            "order_id": "10001",
            "reason": "用户取消订单",
        },
        confirmed=True,
    )
    print(result)


if __name__ == "__main__":
    main()