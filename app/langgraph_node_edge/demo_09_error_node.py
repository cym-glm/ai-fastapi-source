import asyncio
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_node_edge.mock_services import create_initial_state
from app.langgraph_node_edge.schemas import EcommerceNodeEdgeState


async def risky_tool_node(state: EcommerceNodeEdgeState) -> dict:
    try:
        if "异常" in state["user_question"]:
            raise RuntimeError("模拟工具调用失败")

        return {
            "logs": ["risky_tool_node：工具调用成功"],
            "final_answer": "工具调用成功，正常返回结果。",
            "is_finished": True,
        }

    except Exception as exc:
        return {
            "errors": [repr(exc)],
            "logs": ["risky_tool_node：工具调用失败"],
        }


def route_after_risky_tool(
    state: EcommerceNodeEdgeState,
) -> Literal["error_handler", "end"]:
    if state["errors"]:
        return "error_handler"

    return "end"


def error_handler_node(state: EcommerceNodeEdgeState) -> dict:
    return {
        "final_answer": "当前服务暂时异常，请稍后再试，或联系人工客服。",
        "is_finished": True,
        "logs": ["error_handler_node：已生成兜底回答"],
    }


def build_graph():
    graph = StateGraph(EcommerceNodeEdgeState)

    graph.add_node("risky_tool", risky_tool_node)
    graph.add_node("error_handler", error_handler_node)

    graph.add_edge(START, "risky_tool")

    graph.add_conditional_edges(
        "risky_tool",
        route_after_risky_tool,
        {
            "error_handler": "error_handler",
            "end": END,
        },
    )

    graph.add_edge("error_handler", END)

    return graph.compile()


async def main():
    app = build_graph()

    for question in ["正常问题", "这个问题会触发异常"]:
        result = await app.ainvoke(
            create_initial_state(question)
        )

        print("question:", question)
        print("final_answer:", result["final_answer"])
        print("errors:", result["errors"])
        print("logs:", result["logs"])
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())