

from langchain_core.tools  import tool


@tool
def query_order(order_id: str) -> str:
    """根据订单号查询订单状态和物流信息。"""
    # 自己业务逻辑 ---查数据 第三方接口  javva ts python  go
    if order_id == "10001":
        return "订单 10001 已发货，物流公司顺丰，物流单号 SF10001。"

    if order_id == "10002":
        return "订单 10002 已付款，当前待发货。"

    return f"未查询到订单 {order_id}。"


def main():
    print("tool name:", query_order.name)
    print("tool description:", query_order.description)
    print("tool args:", query_order.args)

    result = query_order.invoke({
        "order_id": "10003",
    })

    print("result:", result)


if __name__ == "__main__":
    main()