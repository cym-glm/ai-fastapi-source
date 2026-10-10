from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_routing.mock_services import create_initial_state
from app.langgraph_routing.schemas import RoutingState


def extract_order_id_node(state: RoutingState) -> dict:
    question = state["user_question"]

    if "10001" in question:
        order_id = "10001"
    elif "10002" in question:
        order_id = "10002"
    else:
        order_id = None

    return {
        "order_id": order_id,
        "logs": [f"extract_order_id：order_id={order_id}"],
    }


def route_after_extract_order_id(
    state: RoutingState,
) -> Literal["ask_order_id", "query_order"]:
    if not state["order_id"]:
        return "ask_order_id"

    return "query_order"


def ask_order_id_node(state: RoutingState) -> dict:
    return {
        "final_answer": "请您提供订单号，我才能继续查询。",
        "is_finished": True,
        "logs": ["ask_order_id：缺少订单号，追问用户"],
    }


def query_order_entry_node(state: RoutingState) -> dict:
    return {
        "final_answer": f"已提取订单号 {state['order_id']}，下一步可以查询订单。",
        "logs": ["query_order_entry：进入订单查询流程"],
    }


def build_graph():
    graph = StateGraph(RoutingState)

    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("ask_order_id", ask_order_id_node)
    graph.add_node("query_order_entry", query_order_entry_node)

    graph.add_edge(START, "extract_order_id")

    graph.add_conditional_edges(
        "extract_order_id",
        route_after_extract_order_id,
        {
            "ask_order_id": "ask_order_id",
            "query_order": "query_order_entry",
        },
    )

    graph.add_edge("ask_order_id", END)
    graph.add_edge("query_order_entry", END)

    return graph.compile()


def main():
    app = build_graph()

    questions = [
        "帮我查一下订单 10001。",
        "帮我查一下订单。",
    ]

    for question in questions:
        result = app.invoke(create_initial_state(question))

        print("question:", question)
        print("order_id:", result["order_id"])
        print("final_answer:", result["final_answer"])
        print("logs:", result["logs"])
        print("=" * 80)


if __name__ == "__main__":
    main()