from app.mcp_server_dev.service import mcp_server_dev_service


def main():
    mcp_server_dev_service.call_tool(
        tool_name="query_order_status",
        arguments={
            "order_id": "10001",
        },
        role="customer_service",
        user_id="u_10001",
    )

    mcp_server_dev_service.call_tool(
        tool_name="query_customer_profile",
        arguments={
            "mobile": "13800000000",
        },
        role="customer_service",
        user_id="u_10001",
    )

    logs = mcp_server_dev_service.list_logs()

    print("tool call logs:")
    for log in logs:
        print(log)


if __name__ == "__main__":
    main()