from app.mcp_server_dev.service import mcp_server_dev_service


def main():
    print("prompts:")
    for prompt in mcp_server_dev_service.list_prompts():
        print(prompt)

    print("=" * 100)

    resource = mcp_server_dev_service.read_resource(
        uri="policy://refund",
        role="customer_service",
    )

    prompt = mcp_server_dev_service.render_prompt(
        name="customer_service_reply",
        arguments={
            "question": "订单未发货可以退款吗？",
            "context": resource["content"],
        },
    )

    print("rendered prompt:")
    print(prompt)


if __name__ == "__main__":
    main()