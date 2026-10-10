from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_routing.mock_services import create_initial_state
from app.langgraph_routing.schemas import RoutingState


def assess_risk_node(state: RoutingState) -> dict:
    question = state["user_question"]

    if "大额" in question or "1000" in question:
        return {
            "risk_level": "high",
            "need_human_confirm": True,
            "pending_action": "refund_order",
            "logs": ["assess_risk：高风险，需要人工确认"],
        }

    return {
        "risk_level": "low",
        "need_human_confirm": False,
        "pending_action": None,
        "logs": ["assess_risk：低风险，可自动处理"],
    }


def route_after_risk(
    state: RoutingState,
) -> Literal["human_confirm", "auto_answer"]:
    if state["need_human_confirm"]:
        return "human_confirm"

    return "auto_answer"


def human_confirm_node(state: RoutingState) -> dict:
    return {
        "final_answer": "该操作风险较高，需要人工客服确认后继续处理。",
        "is_finished": True,
        "logs": ["human_confirm：等待人工确认"],
    }


def auto_answer_node(state: RoutingState) -> dict:
    return {
        "final_answer": "该请求风险较低，可以继续自动处理。",
        "is_finished": True,
        "logs": ["auto_answer：自动处理"],
    }


def build_graph():
    graph = StateGraph(RoutingState)

    graph.add_node("assess_risk", assess_risk_node)
    graph.add_node("human_confirm", human_confirm_node)
    graph.add_node("auto_answer", auto_answer_node)

    graph.add_edge(START, "assess_risk")

    graph.add_conditional_edges(
        "assess_risk",
        route_after_risk,
        {
            "human_confirm": "human_confirm",
            "auto_answer": "auto_answer",
        },
    )

    graph.add_edge("human_confirm", END)
    graph.add_edge("auto_answer", END)

    return graph.compile()


def main():
    app = build_graph()

    questions = [
        "我要退款。",
        "我要申请大额退款 1000 元。",
    ]

    for question in questions:
        result = app.invoke(create_initial_state(question))

        print("question:", question)
        print("risk_level:", result["risk_level"])
        print("need_human_confirm:", result["need_human_confirm"])
        print("final_answer:", result["final_answer"])
        print("logs:", result["logs"])
        print("=" * 80)


if __name__ == "__main__":
    main()