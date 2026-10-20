from pathlib import Path


class MockOrderSystem:
    def query_order_status(
        self,
        order_id: str,
    ) -> dict:
        orders = {
            "10001": {
                "order_id": "10001",
                "status": "shipped",
                "amount": 299,
                "logistics": "顺丰快递，运输中",
                "can_refund": False,
            },
            "10002": {
                "order_id": "10002",
                "status": "pending_payment",
                "amount": 99,
                "logistics": None,
                "can_refund": True,
            },
            "10003": {
                "order_id": "10003",
                "status": "not_shipped",
                "amount": 168,
                "logistics": None,
                "can_refund": True,
            },
        }

        return orders.get(
            order_id,
            {
                "order_id": order_id,
                "status": "not_found",
                "message": "未找到该订单。",
            },
        )

    def refund_order(
        self,
        order_id: str,
        reason: str,
    ) -> dict:
        order = self.query_order_status(order_id)

        if order.get("status") == "not_found":
            return {
                "success": False,
                "message": "订单不存在，无法退款。",
            }

        if not order.get("can_refund"):
            return {
                "success": False,
                "message": "当前订单状态不支持直接退款，需要走售后流程。",
            }

        return {
            "success": True,
            "order_id": order_id,
            "refund_status": "refund_requested",
            "reason": reason,
        }


class MockCRMSystem:
    def query_customer(
        self,
        mobile: str,
    ) -> dict:
        return {
            "mobile": mobile,
            "level": "VIP",
            "tags": ["高价值客户", "售后敏感"],
            "recent_orders": ["10001", "10003"],
        }


class MockKnowledgeBaseSystem:
    def __init__(
        self,
        data_dir: str = "data/mcp_server_dev",
    ):
        """初始化模拟知识库系统。

        Args:
            data_dir: 知识库数据文件所在目录，默认为 "data/mcp_server_dev"。
        """
        self.data_dir = Path(data_dir)

    def search_policy(
        self,
        query: str,
    ) -> list[dict]:
        docs = [
            {
                "title": "退款规则",
                "file": "refund_policy.md",
                "keywords": ["退款", "售后", "取消订单"],
            },
            {
                "title": "物流规则",
                "file": "logistics_policy.md",
                "keywords": ["物流", "快递", "签收"],
            },
        ]

        results = []

        for doc in docs:
            if any(keyword in query for keyword in doc["keywords"]):
                path = self.data_dir / doc["file"]
                content = path.read_text(encoding="utf-8")

                results.append(
                    {
                        "title": doc["title"],
                        "content": content,
                        "source_path": str(path),
                    }
                )

        if not results:
            results.append(
                {
                    "title": "默认规则",
                    "content": "暂时没有找到完全匹配的规则，需要人工客服进一步确认。",
                    "source_path": None,
                }
            )

        return results

    def read_policy(
        self,
        name: str,
    ) -> str:
        file_map = {
            "refund": "refund_policy.md",
            "logistics": "logistics_policy.md",
        }

        file_name = file_map.get(name)

        if not file_name:
            raise FileNotFoundError(
                f"政策文档不存在：{name}"
            )

        return (self.data_dir / file_name).read_text(
            encoding="utf-8"
        )