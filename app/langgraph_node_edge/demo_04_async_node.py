import asyncio
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class AsyncNodeState(TypedDict):
    user_question: str
    order_id: str | None
    order_status: str
    final_answer: str


async def extract_order_id_node(state: AsyncNodeState) -> dict:
    await asyncio.sleep(0.05)

    if "10001" in state["user_question"]:
        return {"order_id": "10001"}

    return {"order_id": None}


async def query_order_node(state: AsyncNodeState) -> dict:
    await asyncio.sleep(0.05)

    if state["order_id"] == "10001":
        return {"order_status": "已发货"}

    return {"order_status": "未查询到订单"}


async def answer_node(state: AsyncNodeState) -> dict:
    await asyncio.sleep(0.05)

    return {
        "final_answer": f"订单状态：{state['order_status']}"
    }


def build_graph():
    graph = StateGraph(AsyncNodeState)

    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("query_order", query_order_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "extract_order_id")
    graph.add_edge("extract_order_id", "query_order")
    graph.add_edge("query_order", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


async def main():
    app = build_graph()

    result = await app.ainvoke({
        "user_question": "帮我查一下订单 10001。",
        "order_id": None,
        "order_status": "",
        "final_answer": "",
    })

    print(result)


if __name__ == "__main__":
    asyncio.run(main())