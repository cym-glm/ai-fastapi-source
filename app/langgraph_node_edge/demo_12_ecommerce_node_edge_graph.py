import asyncio
from typing import Literal

from langgraph.graph import END, START, StateGraph
from app.langgraph_node_edge.mock_services import (
    create_initial_state,
    mock_query_order,
    mock_retrieve_policy,
)
from app.langgraph_node_edge.schemas import EcommerceNodeEdgeState


def classify_intent_node(state: EcommerceNodeEdgeState) -> dict:
    question = state["user_question"]

    if "人工" in question:
        intent = "human_service"
    elif "退款" in question or "退货" in question:
        intent = "refund"
    elif "物流" in question:
        intent = "logistics"
    elif "订单" in question:
        intent = "query_order"
    else:
        intent = "general"

    return {
        "intent": intent,
        "logs": [f"classify_intent：{intent}"],
    }


def route_by_intent(
    state: EcommerceNodeEdgeState,
) -> Literal["general", "human", "need_order"]:
    if state["intent"] == "general":
        return "general"

    if state["intent"] == "human_service":
        return "human"

    return "need_order"


def general_answer_node(state: EcommerceNodeEdgeState) -> dict:
    return {
        "final_answer": "这是一个普通问题，可以走普通 ChatModel 生成回答。",
        "is_finished": True,
        "logs": ["general_answer：普通回答完成"],
    }


def transfer_human_node(state: EcommerceNodeEdgeState) -> dict:
    return {
        "final_answer": "我已经为您转接人工客服，请稍等。",
        "is_finished": True,
        "tool_calls": [
            {
                "name": "transfer_human",
                "args": {
                    "reason": state["user_question"],
                },
                "id": "tool_call_transfer_human_001",
                "success": True,
                "result_preview": "已创建人工客服工单",
            }
        ],
        "logs": ["transfer_human：已创建人工客服工单"],
    }


def extract_order_id_node(state: EcommerceNodeEdgeState) -> dict:
    question = state["user_question"]

    if "10001" in question:
        order_id = "10001"
    elif "10002" in question:
        order_id = "10002"
    else:
        order_id = None

    return {
        "order_id": order_id,
        "logs": [f"extract_order_id：{order_id}"],
    }


def route_after_extract_order_id(
    state: EcommerceNodeEdgeState,
) -> Literal["ask_order_id", "query_order"]:
    if not state["order_id"]:
        return "ask_order_id"

    return "query_order"


def ask_order_id_node(state: EcommerceNodeEdgeState) -> dict:
    return {
        "final_answer": "请您提供订单号，我才能继续查询订单状态。",
        "is_finished": True,
        "logs": ["ask_order_id：缺少订单号"],
    }


async def query_order_node(state: EcommerceNodeEdgeState) -> dict:
    # 此处仅为演示，实际使用时应该调用外部 API 查询订单信息
    order_info = await mock_query_order(
        order_id=state["order_id"]
    )

    return {
        "order_info": order_info,
        "tool_calls": [
            {
                "name": "query_order",
                "args": {
                    "order_id": state["order_id"],
                },
                "id": "tool_call_query_order_001",
                "success": True,
                "result_preview": order_info["status_text"],
            }
        ],
        "logs": [f"query_order：{order_info['status_text']}"],
    }


def route_after_query_order(
    state: EcommerceNodeEdgeState,
) -> Literal["retrieve_policy", "generate_order_answer", "error_handler"]:
    order_info = state["order_info"]

    if not order_info:
        return "error_handler"

    if order_info["status"] == "not_found":
        return "generate_order_answer"

    if state["intent"] == "refund":
        return "retrieve_policy"

    return "generate_order_answer"


async def retrieve_policy_node(state: EcommerceNodeEdgeState) -> dict:
    order_info = state["order_info"]

    policy_result = await mock_retrieve_policy(
        order_status=order_info.get("status"),
    )

    return {
        "policy_query": policy_result["policy_query"],
        "policy_answer": policy_result["policy_answer"],
        "sources": policy_result["sources"],
        "logs": ["retrieve_policy：完成规则检索"],
    }


def assess_risk_node(state: EcommerceNodeEdgeState) -> dict:
    order_info = state["order_info"]

    if state["intent"] == "refund" and order_info["status"] == "shipped":
        return {
            "risk_level": "medium",
            "need_human_confirm": False,
            "pending_action": None,
            "logs": ["assess_risk：已发货退款，建议用户收货后申请退货退款"],
        }

    return {
        "risk_level": "low",
        "need_human_confirm": False,
        "pending_action": None,
        "logs": ["assess_risk：低风险"],
    }


def route_after_assess_risk(
    state: EcommerceNodeEdgeState,
) -> Literal["human_confirm", "generate_refund_answer"]:
    if state["need_human_confirm"]:
        return "human_confirm"

    return "generate_refund_answer"


def human_confirm_node(state: EcommerceNodeEdgeState) -> dict:
    return {
        "final_answer": "该操作需要人工确认，我已经为您提交人工处理。",
        "is_finished": True,
        "logs": ["human_confirm：进入人工确认"],
    }


def generate_order_answer_node(state: EcommerceNodeEdgeState) -> dict:
    order_info = state["order_info"]

    if order_info["status"] == "not_found":
        answer = "没有查询到该订单，请您检查订单号是否正确。"
    else:
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
        "logs": ["generate_order_answer：订单回答完成"],
    }


def generate_refund_answer_node(state: EcommerceNodeEdgeState) -> dict:
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
        "logs": ["generate_refund_answer：退款回答完成"],
    }


def error_handler_node(state: EcommerceNodeEdgeState) -> dict:
    return {
        "final_answer": "当前处理失败，请稍后再试，或联系人工客服。",
        "is_finished": True,
        "errors": ["order_info 为空"],
        "logs": ["error_handler：兜底处理"],
    }


def build_graph():
    graph = StateGraph(EcommerceNodeEdgeState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("general_answer", general_answer_node)
    graph.add_node("transfer_human", transfer_human_node)
    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("ask_order_id", ask_order_id_node)
    graph.add_node("query_order", query_order_node)
    graph.add_node("retrieve_policy", retrieve_policy_node)
    graph.add_node("assess_risk", assess_risk_node)
    graph.add_node("human_confirm", human_confirm_node)
    graph.add_node("generate_order_answer", generate_order_answer_node)
    graph.add_node("generate_refund_answer", generate_refund_answer_node)
    graph.add_node("error_handler", error_handler_node)

    graph.add_edge(START, "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "general": "general_answer",
            "human": "transfer_human",
            "need_order": "extract_order_id",
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
            "retrieve_policy": "retrieve_policy",
            "generate_order_answer": "generate_order_answer",
            "error_handler": "error_handler",
        },
    )

    graph.add_edge("retrieve_policy", "assess_risk")

    graph.add_conditional_edges(
        "assess_risk",
        route_after_assess_risk,
        {
            "human_confirm": "human_confirm",
            "generate_refund_answer": "generate_refund_answer",
        },
    )

    graph.add_edge("general_answer", END)
    graph.add_edge("transfer_human", END)
    graph.add_edge("ask_order_id", END)
    graph.add_edge("generate_order_answer", END)
    graph.add_edge("generate_refund_answer", END)
    graph.add_edge("human_confirm", END)
    graph.add_edge("error_handler", END)

    return graph.compile()


async def main():
    app = build_graph()

    questions = [
        "你好，介绍一下 LangGraph。",
        "帮我查一下订单 10001。",
        "我的订单 10002 还没发货，可以退款吗？",
        "我要退款，但是忘记订单号了。",
        "我要找人工客服。",
    ]

    for question in questions:
        print("question:", question)
        print("=" * 80)

        result = await app.ainvoke(
            create_initial_state(question),
            config={
                "recursion_limit": 20
            },
        )

        print("final_answer:")
        print(result["final_answer"])

        print("\nlogs:")
        for log in result["logs"]:
            print("-", log)

        print("\ntool_calls:")
        for tool_call in result["tool_calls"]:
            print("-", tool_call)

        print("\nsources:")
        for source in result["sources"]:
            print("-", source)

        print("=" * 120)


if __name__ == "__main__":
    asyncio.run(main())