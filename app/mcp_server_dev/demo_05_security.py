from app.mcp_server_dev.service import mcp_server_dev_service


def main():
    print("customer_service 尝试调用 refund_order:")
    result = mcp_server_dev_service.call_tool(
        tool_name="refund_order",
        arguments={
            "order_id": "10003",
            "reason": "用户取消订单",
        },
        role="customer_service",
        user_id="u_10001",
        confirmed=True,
    )
    print(result)

    print("=" * 100)

    print("admin 调用 refund_order，但未确认:")
    result = mcp_server_dev_service.call_tool(
        tool_name="refund_order",
        arguments={
            "order_id": "10003",
            "reason": "用户取消订单",
        },
        role="admin",
        user_id="admin_001",
        confirmed=False,
    )
    print(result)

    print("=" * 100)

    print("admin 调用 refund_order，已确认:")
    result = mcp_server_dev_service.call_tool(
        tool_name="refund_order",
        arguments={
            "order_id": "10003",
            "reason": "用户取消订单",
        },
        role="admin",
        user_id="admin_001",
        confirmed=True,
    )
    print(result)


if __name__ == "__main__":
    main()