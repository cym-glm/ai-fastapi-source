from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_routing.mock_services import create_initial_state
from app.langgraph_routing.schemas import RoutingState


def call_unstable_tool_node(state: RoutingState) -> dict:
    retry_count = state["retry_count"]

    if retry_count < 4:
        return {
            "tool_success": False,
            "retry_count": retry_count + 1,
            "errors": [f"第 {retry_count + 1} 次工具调用失败"],
            "logs": [f"call_unstable_tool：失败 retry_count={retry_count + 1}"],
        }

    return {
        "tool_success": True,
        "logs": ["call_unstable_tool：工具调用成功"],
    }


def route_after_unstable_tool(
    state: RoutingState,
) -> Literal["retry", "success", "fallback"]:
    if state["tool_success"]:
        return "success"

    if state["retry_count"] < state["max_retry"]:
        return "retry"

    return "fallback"


def success_node(state: RoutingState) -> dict:
    return {
        "final_answer": "工具调用成功，已完成处理。",
        "is_finished": True,
        "logs": ["success：处理完成"],
    }


def fallback_node(state: RoutingState) -> dict:
    return {
        "final_answer": "工具多次调用失败，请稍后再试或联系人工客服。",
        "is_finished": True,
        "logs": ["fallback：超过最大重试次数"],
    }


def build_graph():
    graph = StateGraph(RoutingState)

    graph.add_node("call_unstable_tool", call_unstable_tool_node)
    graph.add_node("success", success_node)
    graph.add_node("fallback", fallback_node)

    graph.add_edge(START, "call_unstable_tool")

    graph.add_conditional_edges(
        "call_unstable_tool",
        route_after_unstable_tool,
        {
            "retry": "call_unstable_tool",
            "success": "success",
            "fallback": "fallback",
        },
    )

    graph.add_edge("success", END)
    graph.add_edge("fallback", END)

    return graph.compile()


def main():
    app = build_graph()

    state = create_initial_state("测试不稳定工具。")
    state["max_retry"] = 6

    result = app.invoke(
        state,
        config={
            "recursion_limit": 10
        },
    )

    print("final_answer:", result["final_answer"])
    print("retry_count:", result["retry_count"])
    print("errors:")
    for error in result["errors"]:
        print("-", error)

    print("logs:")
    for log in result["logs"]:
        print("-", log)


if __name__ == "__main__":
    main()