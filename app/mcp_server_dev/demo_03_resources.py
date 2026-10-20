from app.mcp_server_dev.service import mcp_server_dev_service


def main():
    print("resources:")
    for resource in mcp_server_dev_service.list_resources("customer_service"):
        print(resource)

    print("=" * 100)

    refund = mcp_server_dev_service.read_resource(
        uri="policy://refund",
        role="customer_service",
    )

    print("policy://refund:")
    print(refund)


if __name__ == "__main__":
    main()