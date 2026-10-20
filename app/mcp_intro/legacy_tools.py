class LegacyOrderApi:
    def get_order(self, order_id: str) -> dict:
        return {
            "order_id": order_id,
            "status": "shipped",
            "logistics": "顺丰快递，运输中",
        }


class LegacyKnowledgeBaseApi:
    def search_docs(self, keyword: str) -> list[dict]:
        return [
            {
                "title": "退款规则",
                "content": "订单未发货可以申请退款，已发货需要走售后流程。",
            },
            {
                "title": "物流规则",
                "content": "物流超过 7 天未更新，可以联系人工客服排查。",
            },
        ]


class LegacyCrmApi:
    def get_customer(self, mobile: str) -> dict:
        return {
            "mobile": mobile,
            "level": "VIP",
            "tags": ["高价值客户", "售后敏感"],
        }


def openai_tool_adapter_for_order(order_id: str) -> str:
    api = LegacyOrderApi()
    return str(api.get_order(order_id))


def claude_tool_adapter_for_order(params: dict) -> str:
    api = LegacyOrderApi()
    return str(api.get_order(params["order_id"]))


def langchain_tool_adapter_for_order(order_id: str) -> str:
    api = LegacyOrderApi()
    result = api.get_order(order_id)
    return f"订单 {result['order_id']} 当前状态：{result['status']}"