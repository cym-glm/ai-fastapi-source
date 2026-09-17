from app.prompts.base import (
    PromptMessageTemplate,
    PromptRole,
    PromptScenario,
    PromptTemplate,
)
from app.prompts.examples import ECOMMERCE_FEW_SHOT_EXAMPLES


ECOMMERCE_CUSTOMER_SERVICE_PROMPT_V1 = PromptTemplate(
    prompt_id="ecommerce_customer_service",
    name="跨境电商客服助手",
    scenario=PromptScenario.ECOMMERCE_CUSTOMER_SERVICE,
    version="v1",
    description="用于跨境电商客服场景，处理订单、物流、售后等问题。",
    required_variables=[
        "user_question",
        "business_rules",
        "order_info",
    ],
    messages=[
        PromptMessageTemplate(
            role=PromptRole.SYSTEM,
            template=(
                "你是一个跨境电商平台的专业客服助手。\n"
                "\n"
                "你的职责：\n"
                "1. 帮助用户解答订单、物流、退款、售后相关问题。\n"
                "2. 回答要礼貌、清晰、简洁。\n"
                "3. 如果需要订单号，但用户没有提供，要先引导用户提供订单号。\n"
                "4. 不能编造订单状态、物流单号、退款进度。\n"
                "5. 如果订单信息为空或不足，要明确说明无法确认，并引导用户补充信息。\n"
                "6. 如果问题超出客服范围，要建议用户转人工客服。\n"
                "\n"
                "业务规则：\n"
                "{business_rules}\n"
                "\n"
                "参考示例：\n"
                f"{ECOMMERCE_FEW_SHOT_EXAMPLES}"
            )
        ),
        PromptMessageTemplate(
            role=PromptRole.USER,
            template=(
                "用户问题：\n"
                "{user_question}\n"
                "\n"
                "订单信息：\n"
                "{order_info}\n"
                "\n"
                "请根据以上信息回复用户。"
            ),
        ),
    ],
)