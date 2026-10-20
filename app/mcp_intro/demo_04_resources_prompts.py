from app.mcp_intro.service import mcp_intro_service


def main():
    print("resources:")
    for item in mcp_intro_service.list_resources():
        print(item)

    print("=" * 80)
    print("read resource:")
    resource = mcp_intro_service.read_resource(
        "kb://refund-policy"
    )
    print(resource)

    print("=" * 80)
    print("prompts:")
    for item in mcp_intro_service.list_prompts():
        print(item)

    print("=" * 80)
    print("render prompt:")
    prompt = mcp_intro_service.get_prompt(
        name="customer_service_reply",
        arguments={
            "question": "订单未发货可以退款吗？",
            "context": resource["content"],
        },
    )
    print(prompt)


if __name__ == "__main__":
    main()