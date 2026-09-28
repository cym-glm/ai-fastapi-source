import asyncio

from langgraph.graph import END, START, StateGraph




from app.langgraph_node_edge.mock_services import (
    create_initial_state,
    mock_query_order,
)
from app.langgraph_node_edge.schemas import EcommerceNodeEdgeState


def extract_order_id_node(state: EcommerceNodeEdgeState) -> dict:
    question = state["user_question"]

    if "10001" in question:
        order_id = "10001"
    elif "10002" in question:
        order_id = "10002"
    else:
        order_id = None

    return {
        "order_id": order_id,
        "logs": [f"extract_order_id：订单号为 {order_id}"],
    }


async def query_order_tool_node(
    state: EcommerceNodeEdgeState,
) -> dict:
    # 模拟的业务接口，  真实业务即可 --   springboot fastapi 
    order_info = await mock_query_order(
        order_id=state["order_id"]
    )

    return {
        "order_info": order_info,
        "tool_calls": [
            {
                "name": "query_order",
                "args": {
                    "order_id": state["order_id"],
                },
                "id": "tool_call_query_order_001",
                "success": True,
                "result_preview": order_info["status_text"],
            }
        ],
        "logs": [
            f"query_order_tool_node：{order_info['status_text']}"
        ],
    }


def answer_node(state: EcommerceNodeEdgeState) -> dict:
    order_info = state["order_info"]

    return {
        "final_answer": f"您的订单状态是：{order_info['status_text']}。",
        "is_finished": True,
        "logs": ["answer_node：订单回答生成完成"],
    }


def build_graph():
    graph = StateGraph(EcommerceNodeEdgeState)

    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("query_order", query_order_tool_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "extract_order_id")
    graph.add_edge("extract_order_id", "query_order")
    graph.add_edge("query_order", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


async def main():
    app = build_graph()

    result = await app.ainvoke(
        create_initial_state("帮我查一下订单 10001。")
    )

    print("final_answer:", result["final_answer"])
    print("tool_calls:", result["tool_calls"])
    print("logs:", result["logs"])


if __name__ == "__main__":
    asyncio.run(main())