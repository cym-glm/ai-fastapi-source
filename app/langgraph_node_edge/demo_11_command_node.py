from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class CommandRouteState(TypedDict):
    user_question: str
    intent: str
    final_answer: str


def router_node(
    state: CommandRouteState,
) -> Command[Literal["general_node", "refund_node"]]:
    question = state["user_question"]

    if "退款" in question:
        return Command(
            update={
                "intent": "refund"
            },
            goto="refund_node",
        )

    return Command(
        update={
            "intent": "general"
        },
        goto="general_node",
    )


def general_node(state: CommandRouteState) -> dict:
    return {
        "final_answer": "这是普通问题。"
    }


def refund_node(state: CommandRouteState) -> dict:
    return {
        "final_answer": "这是退款问题，需要进入订单和售后规则流程。"
    }


def build_graph():
    graph = StateGraph(CommandRouteState)

    graph.add_node("router", router_node)
    graph.add_node("general_node", general_node)
    graph.add_node("refund_node", refund_node)

    graph.add_edge(START, "router")
    graph.add_edge("general_node", END)
    graph.add_edge("refund_node", END)

    return graph.compile()


def main():
    app = build_graph()

    for question in ["你好", "我的订单可以退款吗？"]:
        result = app.invoke({
            "user_question": question,
            "intent": "unknown",
            "final_answer": "",
        })

        print("question:", question)
        print(result)
        print("=" * 80)


if __name__ == "__main__":
    main()