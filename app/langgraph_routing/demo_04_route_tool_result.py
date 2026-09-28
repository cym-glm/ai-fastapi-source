import asyncio
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_routing.mock_services import (
    create_initial_state,
    mock_query_order,
)
from app.langgraph_routing.schemas import RoutingState


def extract_order_id_node(state: RoutingState) -> dict:
    question = state["user_question"]

    if "10001" in question:
        order_id = "10001"
    elif "99999" in question:
        order_id = "99999"
    else:
        order_id = None

    return {
        "order_id": order_id,
        "logs": [f"extract_order_id：order_id={order_id}"],
    }


async def query_order_node(state: RoutingState) -> dict:
    # 异步查询订单信息,  真实的查询业务接口  （）
    result = await mock_query_order(state["order_id"])

    if not result["success"]:
        return {
            "tool_success": False,
            "order_info": result.get("data"),
            "errors": [result["error"]],
            "tool_calls": [
                {
                    "name": "query_order",
                    "args": {"order_id": state["order_id"]},
                    "success": False,
                    "result_preview": result["error"],
                }
            ],
            "logs": [f"query_order：失败 {result['error']}"],
        }

    return {
        "tool_success": True,
        "order_info": result["data"],
        "tool_calls": [
            {
                "name": "query_order",
                "args": {"order_id": state["order_id"]},
                "success": True,
                "result_preview": result["data"]["status_text"],
            }
        ],
        "logs": [f"query_order：成功 {result['data']['status_text']}"],
    }


def route_after_query_order(
    state: RoutingState,
) -> Literal["success", "not_found", "error"]:
    if state["tool_success"]:
        return "success"

    if state["errors"] and "order_not_found" in state["errors"]:
        return "not_found"

    return "error"


def order_success_node(state: RoutingState) -> dict:
    return {
        "final_answer": f"您的订单状态是：{state['order_info']['status_text']}。",
        "is_finished": True,
        "logs": ["order_success：订单查询成功"],
    }


def order_not_found_node(state: RoutingState) -> dict:
    return {
        "final_answer": "没有查询到该订单，请检查订单号是否正确。",
        "is_finished": True,
        "logs": ["order_not_found：订单不存在"],
    }


def error_handler_node(state: RoutingState) -> dict:
    return {
        "final_answer": "订单查询服务暂时异常，请稍后再试。",
        "is_finished": True,
        "logs": ["error_handler：工具失败兜底"],
    }


def build_graph():
    graph = StateGraph(RoutingState)

    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("query_order", query_order_node)
    graph.add_node("order_success", order_success_node)
    graph.add_node("order_not_found", order_not_found_node)
    graph.add_node("error_handler", error_handler_node)

    graph.add_edge(START, "extract_order_id")
    graph.add_edge("extract_order_id", "query_order")

    graph.add_conditional_edges(
        "query_order",
        route_after_query_order,
        {
            "success": "order_success",
            "not_found": "order_not_found",
            "error": "error_handler",
        },
    )

    graph.add_edge("order_success", END)
    graph.add_edge("order_not_found", END)
    graph.add_edge("error_handler", END)

    return graph.compile()


async def main():
    app = build_graph()

    for question in ["帮我查一下订单 10001。", "帮我查一下订单 99999。"]:
        result = await app.ainvoke(create_initial_state(question))

        print("question:", question)
        print("final_answer:", result["final_answer"])
        print("errors:", result["errors"])
        print("logs:", result["logs"])
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())