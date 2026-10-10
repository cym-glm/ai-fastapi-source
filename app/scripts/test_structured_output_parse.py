from app.structured_outputs.parser import parse_structured_output
from app.structured_outputs.schemas import IntentClassificationOutput


def main():
    raw_text = """
        ```json
            {
            "intent": "query_order",
            "confidence": 0.92,
            "need_order_id": true,
            "reply_strategy": "ask_order_id",
            "reason": "用户在询问订单状态，但是没有提供订单号。"
            }
        """
    result = parse_structured_output(
        raw_text=raw_text,
        schema=IntentClassificationOutput,
    )

    print(result.model_dump())
main()
