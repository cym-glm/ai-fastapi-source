from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class CommandDemoState(TypedDict):
    user_question: str
    intent: str
    final_answer: str


def command_router_node(
    state: CommandDemoState,
) -> Command[Literal["general_node", "refund_node"]]:
    question = state["user_question"]

    if "退款" in question:
        return Command(
            update={"intent": "refund"},
            goto="refund_node",
        )

    return Command(
        update={"intent": "general"},
        goto="general_node",
    )


def general_node(state: CommandDemoState) -> dict:
    return {
        "final_answer": "Command 路由到了普通回答节点。"
    }


def refund_node(state: CommandDemoState) -> dict:
    return {
        "final_answer": "Command 路由到了退款节点。"
    }


def build_graph():
    graph = StateGraph(CommandDemoState)

    graph.add_node("router", command_router_node)
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
            "intent": "",
            "final_answer": "",
        })

        print("question:", question)
        print("intent:", result["intent"])
        print("final_answer:", result["final_answer"])
        print("=" * 80)


if __name__ == "__main__":
    main()