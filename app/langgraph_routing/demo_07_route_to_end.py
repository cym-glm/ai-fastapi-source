from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_routing.mock_services import create_initial_state
from app.langgraph_routing.schemas import RoutingState


def check_finished_node(state: RoutingState) -> dict:
    if "不用处理" in state["user_question"]:
        return {
            "final_answer": "好的，本次不做处理。",
            "is_finished": True,
            "logs": ["check_finished：用户表示不用处理"],
        }

    return {
        "is_finished": False,
        "logs": ["check_finished：需要继续处理"],
    }


def route_after_check_finished(
    state: RoutingState,
) -> Literal["continue", "end"]:
    if state["is_finished"]:
        return "end"

    return "continue"


def continue_node(state: RoutingState) -> dict:
    return {
        "final_answer": "继续进入后续处理流程。",
        "is_finished": True,
        "logs": ["continue_node：继续处理完成"],
    }


def build_graph():
    graph = StateGraph(RoutingState)

    graph.add_node("check_finished", check_finished_node)
    graph.add_node("continue_node", continue_node)

    graph.add_edge(START, "check_finished")

    graph.add_conditional_edges(
        "check_finished",
        route_after_check_finished,
        {
            "continue": "continue_node",
            "end": END,
        },
    )

    graph.add_edge("continue_node", END)

    return graph.compile()


def main():
    app = build_graph()

    questions = [
        "不用处理了。",
        "帮我继续处理订单。",
    ]

    for question in questions:
        result = app.invoke(create_initial_state(question))

        print("question:", question)
        print("final_answer:", result["final_answer"])
        print("logs:", result["logs"])
        print("=" * 80)


if __name__ == "__main__":
    main()