
from langchain_core.tools import tool

@tool
def query_order(order_id: str) -> str:
    """ 根据订单号查询订单和物流的状态。 """
    if order_id == "10001":
        return "订单 10001 的状态是：已发货。 物流公司是：顺丰快递。 物流单号是：1234567890。"
    return f"未查询到订单 {order_id}。"



def run_tool():
    print("tool name: ", query_order.name)
    print("tool __doc__: ", query_order.__doc__)
    print("tool description: ", query_order.description)
    print("tool args: ", query_order.args)

    result = query_order.invoke({
        "order_id": "10001",
    })

    print("tool result: ", result)


if __name__ == "__main__":
    run_tool()