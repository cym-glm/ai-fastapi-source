from app.mcp_server_dev.service import mcp_server_dev_service


def main():
    print("customer_service 可见工具：")
    for tool in mcp_server_dev_service.list_tools("customer_service"):
        print(tool)

    print("=" * 100)

    result = mcp_server_dev_service.call_tool(
        tool_name="query_order_status",
        arguments={
            "order_id": "10001"
        },
        role="customer_service",
        user_id="u_10001",
    )

    print("query_order_status result:")
    print(result)

    print("=" * 100)

    result = mcp_server_dev_service.call_tool(
        tool_name="search_enterprise_policy",
        arguments={
            "query": "订单未发货可以退款吗？"
        },
        role="customer_service",
        user_id="u_10001",
    )

    print("search_enterprise_policy result:")
    print(result)


if __name__ == "__main__":
    main()