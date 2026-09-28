import asyncio
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_routing.mock_services import (
    create_initial_state,
    mock_query_order,
    mock_search_policy,
)
from app.langgraph_routing.schemas import RoutingState


def classify_intent_node(state: RoutingState) -> dict:
    question = state["user_question"]

    if "人工" in question:
        intent = "human_service"
    elif "退款" in question or "退货" in question:
        intent = "refund"
    elif "售后" in question:
        intent = "after_sales"
    elif "物流" in question:
        intent = "logistics"
    elif "订单" in question:
        intent = "query_order"
    else:
        intent = "general"

    return {
        "intent": intent,
        "logs": [f"classify_intent：intent={intent}"],
    }


def route_by_intent(
    state: RoutingState,
) -> Literal["general", "human", "policy_only", "need_order"]:
    intent = state["intent"]

    if intent == "general":
        return "general"

    if intent == "human_service":
        return "human"

    if intent == "after_sales":
        return "policy_only"

    return "need_order"


def general_answer_node(state: RoutingState) -> dict:
    return {
        "final_answer": "这是普通问题，可以走普通 ChatModel。",
        "is_finished": True,
        "logs": ["general_answer：普通回答完成"],
    }


def transfer_human_node(state: RoutingState) -> dict:
    return {
        "final_answer": "我已经为您转接人工客服，请稍等。",
        "is_finished": True,
        "tool_calls": [
            {
                "name": "transfer_human",
                "args": {"reason": state["user_question"]},
                "success": True,
                "result_preview": "已创建人工客服工单",
            }
        ],
        "logs": ["transfer_human：已转人工"],
    }


def build_policy_query_node(state: RoutingState) -> dict:
    question = state["user_question"]

    if state["intent"] == "after_sales":
        query = question
    elif state["order_info"] and state["order_info"].get("status") == "paid":
        query = "订单未发货退款规则"
    elif state["order_info"] and state["order_info"].get("status") in ["shipped", "delivered"]:
        query = "订单已发货退货退款规则"
    else:
        query = "售后规则"

    return {
        "policy_query": query,
        "logs": [f"build_policy_query：policy_query={query}"],
    }


async def retrieve_policy_node(state: RoutingState) -> dict:
    # 这里用的是 mock_search_policy，实际项目中换成实际的 RAG 检索服务
    result = await mock_search_policy(state["policy_query"])

    return {
        "rag_hit": result["hit"],
        "policy_answer": result["answer"],
        "sources": result["sources"],
        "logs": [f"retrieve_policy：rag_hit={result['hit']}"],
    }


def route_after_policy_only(
    state: RoutingState,
) -> Literal["answer_policy", "policy_fallback"]:
    if state["rag_hit"] and state["sources"]:
        return "answer_policy"

    return "policy_fallback"


def answer_policy_node(state: RoutingState) -> dict:
    return {
        "final_answer": f"{state['policy_answer']} 回答依据来自知识库。",
        "is_finished": True,
        "logs": ["answer_policy：知识库回答完成"],
    }


def policy_fallback_node(state: RoutingState) -> dict:
    return {
        "final_answer": "根据当前知识库无法确认，建议联系人工客服。",
        "is_finished": True,
        "logs": ["policy_fallback：知识库未命中"],
    }


def extract_order_id_node(state: RoutingState) -> dict:
    question = state["user_question"]

    if "10001" in question:
        order_id = "10001"
    elif "10002" in question:
        order_id = "10002"
    elif "10003" in question:
        order_id = "10003"
    elif "99999" in question:
        order_id = "99999"
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
        "final_answer": "请您提供订单号，我才能继续查询订单状态。",
        "is_finished": True,
        "logs": ["ask_order_id：缺少订单号"],
    }


async def query_order_node(state: RoutingState) -> dict:
    # 这里用的是 mock_query_order，实际项目中换成实际的订单查询服务
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
) -> Literal["order_not_found", "error", "need_policy", "answer_order"]:
    if not state["tool_success"]:
        if state["errors"] and "order_not_found" in state["errors"]:
            return "order_not_found"

        return "error"

    if state["intent"] == "refund":
        return "need_policy"

    return "answer_order"


def order_not_found_node(state: RoutingState) -> dict:
    return {
        "final_answer": "没有查询到该订单，请检查订单号是否正确。",
        "is_finished": True,
        "logs": ["order_not_found：订单不存在"],
    }


def answer_order_node(state: RoutingState) -> dict:
    order_info = state["order_info"]

    answer = f"您的订单当前状态是：{order_info['status_text']}。"

    if order_info.get("tracking_no"):
        answer += (
            f"物流公司：{order_info['tracking_company']}，"
            f"物流单号：{order_info['tracking_no']}，"
            f"最新节点：{order_info['latest_event']}"
        )

    return {
        "final_answer": answer,
        "is_finished": True,
        "logs": ["answer_order：订单回答完成"],
    }


def route_after_refund_policy(
    state: RoutingState,
) -> Literal["assess_risk", "policy_fallback"]:
    if state["rag_hit"] and state["sources"]:
        return "assess_risk"

    return "policy_fallback"


def assess_risk_node(state: RoutingState) -> dict:
    order_info = state["order_info"]

    if order_info and order_info.get("status") == "delivered":
        return {
            "risk_level": "medium",
            "need_human_confirm": False,
            "pending_action": None,
            "logs": ["assess_risk：已签收订单，建议按退货退款流程处理"],
        }

    if "大额" in state["user_question"]:
        return {
            "risk_level": "high",
            "need_human_confirm": True,
            "pending_action": "refund_order",
            "logs": ["assess_risk：大额退款，需要人工确认"],
        }

    return {
        "risk_level": "low",
        "need_human_confirm": False,
        "pending_action": None,
        "logs": ["assess_risk：低风险"],
    }


def route_after_risk(
    state: RoutingState,
) -> Literal["human_confirm", "answer_refund"]:
    if state["need_human_confirm"]:
        return "human_confirm"

    return "answer_refund"


def human_confirm_node(state: RoutingState) -> dict:
    return {
        "final_answer": "该退款请求需要人工客服确认，我已经为您提交处理。",
        "is_finished": True,
        "logs": ["human_confirm：进入人工确认"],
    }


def answer_refund_node(state: RoutingState) -> dict:
    order_info = state["order_info"]

    answer = (
        f"您的订单当前状态是：{order_info['status_text']}。"
        f"{state['policy_answer']}"
    )

    if state["sources"]:
        answer += " 回答依据来自售后规则知识库。"

    return {
        "final_answer": answer,
        "is_finished": True,
        "logs": ["answer_refund：退款回答完成"],
    }


def error_handler_node(state: RoutingState) -> dict:
    return {
        "final_answer": "当前服务暂时异常，请稍后再试，或联系人工客服。",
        "is_finished": True,
        "logs": ["error_handler：错误兜底"],
    }


def build_graph():
    graph = StateGraph(RoutingState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("general_answer", general_answer_node)
    graph.add_node("transfer_human", transfer_human_node)

    graph.add_node("build_policy_query", build_policy_query_node)
    graph.add_node("retrieve_policy", retrieve_policy_node)
    graph.add_node("answer_policy", answer_policy_node)
    graph.add_node("policy_fallback", policy_fallback_node)

    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("ask_order_id", ask_order_id_node)
    graph.add_node("query_order", query_order_node)
    graph.add_node("order_not_found", order_not_found_node)
    graph.add_node("answer_order", answer_order_node)

    graph.add_node("assess_risk", assess_risk_node)
    graph.add_node("human_confirm", human_confirm_node)
    graph.add_node("answer_refund", answer_refund_node)
    graph.add_node("error_handler", error_handler_node)

    graph.add_edge(START, "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "general": "general_answer",
            "human": "transfer_human",
            "policy_only": "build_policy_query",
            "need_order": "extract_order_id",
        },
    )

    graph.add_edge("build_policy_query", "retrieve_policy")

    graph.add_conditional_edges(
        "retrieve_policy",
        route_after_policy_only,
        {
            "answer_policy": "answer_policy",
            "policy_fallback": "policy_fallback",
        },
    )

    graph.add_conditional_edges(
        "extract_order_id",
        route_after_extract_order_id,
        {
            "ask_order_id": "ask_order_id",
            "query_order": "query_order",
        },
    )

    graph.add_conditional_edges(
        "query_order",
        route_after_query_order,
        {
            "order_not_found": "order_not_found",
            "error": "error_handler",
            "need_policy": "build_policy_query",
            "answer_order": "answer_order",
        },
    )

    graph.add_conditional_edges(
        "retrieve_policy",
        route_after_refund_policy,
        {
            "assess_risk": "assess_risk",
            "policy_fallback": "policy_fallback",
        },
    )

    graph.add_conditional_edges(
        "assess_risk",
        route_after_risk,
        {
            "human_confirm": "human_confirm",
            "answer_refund": "answer_refund",
        },
    )

    graph.add_edge("general_answer", END)
    graph.add_edge("transfer_human", END)
    graph.add_edge("answer_policy", END)
    graph.add_edge("policy_fallback", END)
    graph.add_edge("ask_order_id", END)
    graph.add_edge("order_not_found", END)
    graph.add_edge("answer_order", END)
    graph.add_edge("human_confirm", END)
    graph.add_edge("answer_refund", END)
    graph.add_edge("error_handler", END)

    return graph.compile()


async def main():
    app = build_graph()

    questions = [
        "你好，介绍一下 LangGraph。",
        "我要找人工客服。",
        "售后规则是什么？",
        "帮我查一下订单 10001。",
        "帮我查一下订单。",
        "帮我查一下订单 99999。",
        "我的订单 10002 还没发货，可以退款吗？",
        "我的订单 10003 已经签收，可以退款吗？",
        "我的订单 10002 申请大额退款。",
    ]

    for question in questions:
        print("question:", question)
        print("=" * 80)

        result = await app.ainvoke(
            create_initial_state(question),
            config={
                "recursion_limit": 30
            },
        )

        print("intent:", result["intent"])
        print("final_answer:", result["final_answer"])

        print("\nlogs:")
        for log in result["logs"]:
            print("-", log)

        print("\ntool_calls:")
        for tool_call in result["tool_calls"]:
            print("-", tool_call)

        print("\nsources:")
        for source in result["sources"]:
            print("-", source)

        print("\nerrors:")
        for error in result["errors"]:
            print("-", error)

        print("=" * 120)


if __name__ == "__main__":
    asyncio.run(main())