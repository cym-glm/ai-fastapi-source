from app.prompts.base import PromptScenario
from app.services.prompt_service import prompt_service


def main():
    messages = prompt_service.render_by_scenario(
        scenario=PromptScenario.ECOMMERCE_CUSTOMER_SERVICE,
        variables={
            "user_question": "我的订单怎么还没发货？",
            "business_rules": (
                "1. 普通商品付款后 48 小时内发货。\n"
                "2. 定制商品付款后 7 个工作日内发货。\n"
                "3. 没有订单号时，不能查询具体物流。"
            ),
            "order_info": "用户未提供订单号。",
        },
    )

    for message in messages:
        print("role:", message.role)
        print(message.content)
        print("=" * 60)


if __name__ == "__main__":
    main()