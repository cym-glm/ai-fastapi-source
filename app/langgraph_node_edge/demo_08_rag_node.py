import asyncio

from langgraph.graph import END, START, StateGraph

from app.langgraph_node_edge.mock_services import (
    create_initial_state,
    mock_query_order,
    mock_retrieve_policy,
)
from app.langgraph_node_edge.schemas import EcommerceNodeEdgeState


def extract_order_id_node(state: EcommerceNodeEdgeState) -> dict:
    if "10002" in state["user_question"]:
        return {
            "order_id": "10002",
            "logs": ["extract_order_id：订单号为 10002"],
        }

    return {
        "order_id": None,
        "logs": ["extract_order_id：未提取到订单号"],
    }


async def query_order_node(state: EcommerceNodeEdgeState) -> dict:
    # 模拟的业务接口，  真实业务即可 --   springboot fastapi 
    order_info = await mock_query_order(state["order_id"])

    return {
        "order_info": order_info,
        "logs": [f"query_order：{order_info['status_text']}"],
    }


async def retrieve_policy_rag_node(
    state: EcommerceNodeEdgeState,
) -> dict:
    order_info = state["order_info"]

    # 模拟的业务接口，  真实业务即可 --   springboot fastapi 
    policy_result = await mock_retrieve_policy(
        order_status=order_info.get("status"),
    )

    return {
        "policy_query": policy_result["policy_query"],
        "policy_answer": policy_result["policy_answer"],
        "sources": policy_result["sources"],
        "logs": ["retrieve_policy_rag_node：完成售后规则检索"],
    }


def answer_node(state: EcommerceNodeEdgeState) -> dict:
    order_info = state["order_info"]

    return {
        "final_answer": (
            f"您的订单状态是：{order_info['status_text']}。"
            f"{state['policy_answer']}"
        ),
        "is_finished": True,
        "logs": ["answer_node：最终回答完成"],
    }


def build_graph():
    graph = StateGraph(EcommerceNodeEdgeState)

    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("query_order", query_order_node)
    graph.add_node("retrieve_policy", retrieve_policy_rag_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "extract_order_id")
    graph.add_edge("extract_order_id", "query_order")
    graph.add_edge("query_order", "retrieve_policy")
    graph.add_edge("retrieve_policy", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


async def main():
    app = build_graph()

    result = await app.ainvoke(
        create_initial_state("我的订单 10002 还没发货，可以退款吗？")
    )

    print("final_answer:")
    print(result["final_answer"])

    print("=" * 80)
    print("sources:")
    for source in result["sources"]:
        print(source)

    print("=" * 80)
    print("logs:")
    for log in result["logs"]:
        print("-", log)


if __name__ == "__main__":
    asyncio.run(main())