import asyncio
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_routing.mock_services import (
    create_initial_state,
    mock_search_policy,
)
from app.langgraph_routing.schemas import RoutingState


def build_policy_query_node(state: RoutingState) -> dict:
    question = state["user_question"]

    if "年假" in question:
        query = "员工年假制度"
    elif "退款" in question:
        query = "订单未发货退款规则"
    else:
        query = question

    return {
        "policy_query": query,
        "logs": [f"build_policy_query：query={query}"],
    }


async def retrieve_policy_node(state: RoutingState) -> dict:
    # 异步查询政策信息,  真实的查询业务接口  （） rag查询
    result = await mock_search_policy(state["policy_query"])

    return {
        "rag_hit": result["hit"],
        "policy_answer": result["answer"],
        "sources": result["sources"],
        "logs": [f"retrieve_policy：rag_hit={result['hit']}"],
    }


def route_after_rag(
    state: RoutingState,
) -> Literal["answer_with_sources", "fallback"]:
    if state["rag_hit"] and state["sources"]:
        return "answer_with_sources"

    return "fallback"


def answer_with_sources_node(state: RoutingState) -> dict:
    return {
        "final_answer": (
            f"{state['policy_answer']} 回答依据来自知识库。"
        ),
        "is_finished": True,
        "logs": ["answer_with_sources：基于知识库回答"],
    }


def fallback_node(state: RoutingState) -> dict:
    return {
        "final_answer": "根据当前知识库无法确认，建议联系人工客服。",
        "is_finished": True,
        "logs": ["fallback：知识库未命中，进入兜底"],
    }


def build_graph():
    graph = StateGraph(RoutingState)

    graph.add_node("build_policy_query", build_policy_query_node)
    graph.add_node("retrieve_policy", retrieve_policy_node)
    graph.add_node("answer_with_sources", answer_with_sources_node)
    graph.add_node("fallback", fallback_node)

    graph.add_edge(START, "build_policy_query")
    graph.add_edge("build_policy_query", "retrieve_policy")

    graph.add_conditional_edges(
        "retrieve_policy",
        route_after_rag,
        {
            "answer_with_sources": "answer_with_sources",
            "fallback": "fallback",
        },
    )

    graph.add_edge("answer_with_sources", END)
    graph.add_edge("fallback", END)

    return graph.compile()


async def main():
    app = build_graph()

    questions = [
        "订单未发货可以退款吗？",
        "公司下午茶制度是什么？",
    ]

    for question in questions:
        result = await app.ainvoke(create_initial_state(question))

        print("question:", question)
        print("rag_hit:", result["rag_hit"])
        print("final_answer:", result["final_answer"])
        print("sources:", result["sources"])
        print("logs:", result["logs"])
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())