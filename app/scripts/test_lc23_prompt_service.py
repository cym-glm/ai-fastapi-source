from app.langchain_prompts.service import langchain_prompt_service
from app.prompts.base import PromptScenario


def main():
    print("prompt list:")
    for item in langchain_prompt_service.list_prompts():
        print(item)

    print("=" * 80)

    messages = langchain_prompt_service.render_messages_by_scenario(
        scenario=PromptScenario.ECOMMERCE_CUSTOMER_SERVICE,
        version="v1",
        variables={
            "history": [],
            "user_question": "帮我查一下订单 10001 到哪了？",
            "business_rules": "不能编造物流信息；没有订单号时必须追问。",
            "order_info": "用户提供了订单号 10001。",
        },
    )

    for message in messages:
        print(message.type, ":", message.content)
        print("-" * 80)


if __name__ == "__main__":
    main()