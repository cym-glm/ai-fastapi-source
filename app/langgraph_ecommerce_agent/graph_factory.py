import uuid
from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore
from langgraph.types import interrupt

from app.langgraph_ecommerce_agent.mock_services import (
    extract_order_id_from_text,
    mock_execute_refund,
    mock_query_logistics,
    mock_query_order,
    mock_retrieve_policy,
    mock_transfer_human,
)
from app.langgraph_ecommerce_agent.schemas import (
    EcommerceAgentContext,
    EcommerceAgentState,
)


def recall_memory_node(
    state: EcommerceAgentState,
    runtime: Runtime[EcommerceAgentContext],
) -> dict:
    namespace = (
        runtime.context.tenant_id,
        runtime.context.user_id,
        "preferences",
    )

    items = runtime.store.search(namespace)

    memories = []

    for item in items:
        value = item.value
        memories.append({
            "key": item.key,
            "type": value.get("type", "preference"),
            "content": value.get("content", ""),
            "confidence": value.get("confidence", 0.8),
            "source": value.get("source", "store"),
        })

    return {
        "recalled_memories": memories,
        "logs": [f"recall_memory：召回 {len(memories)} 条用户偏好"],
        "agent_trace": [
            {
                "node_name": "recall_memory",
                "input_summary": "tenant_id + user_id",
                "output_summary": f"召回 {len(memories)} 条偏好",
                "route_to": "classify_intent",
                "reason": "回答前先获取用户长期偏好",
            }
        ],
    }


def classify_intent_node(state: EcommerceAgentState) -> dict:
    question = state["user_question"]

    if "记住" in question or "以后回答" in question or "以后你" in question:
        intent = "remember_preference"
    elif "人工" in question or "客服" in question and "人工" in question:
        intent = "human_service"
    elif "退款" in question or "退货" in question:
        intent = "refund"
    elif "物流" in question or "快递" in question:
        intent = "logistics"
    elif "售后" in question or "规则" in question:
        intent = "after_sales"
    elif "订单" in question:
        intent = "query_order"
    elif state.get("intent") in ["refund", "query_order", "logistics"]:
        # 支持多轮续聊。
        # 比如上一轮问“我要退款”，这一轮只补充“订单号是 10002”。
        intent = state["intent"]
    else:
        intent = "general"

    return {
        "intent": intent,
        "logs": [f"classify_intent：intent={intent}"],
    }


def route_by_intent(
    state: EcommerceAgentState,
) -> Literal[
    "remember",
    "general",
    "human",
    "policy_only",
    "need_order",
]:
    intent = state["intent"]

    if intent == "remember_preference":
        return "remember"

    if intent == "general":
        return "general"

    if intent == "human_service":
        return "human"

    if intent == "after_sales":
        return "policy_only"

    return "need_order"


def write_memory_node(
    state: EcommerceAgentState,
    runtime: Runtime[EcommerceAgentContext],
) -> dict:
    namespace = (
        runtime.context.tenant_id,
        runtime.context.user_id,
        "preferences",
    )

    memory = {
        "type": "preference",
        "content": state["user_question"],
        "confidence": 0.85,
        "source": "user_explicit_request",
    }

    key = f"pref_{uuid.uuid4().hex}"

    runtime.store.put(
        namespace,
        key,
        memory,
    )

    answer = "好的，我已经记住这个偏好。"

    return {
        "new_memories": [
            {
                "key": key,
                **memory,
            }
        ],
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": [f"write_memory：写入用户偏好 key={key}"],
    }


def general_answer_node(state: EcommerceAgentState) -> dict:
    memory_text = "\n".join(
        memory["content"]
        for memory in state["recalled_memories"]
    )

    if memory_text:
        answer = (
            "您好，我可以帮您查询订单、查看物流、咨询退款和售后规则。"
            f"我也会参考你的偏好：{memory_text}"
        )
    else:
        answer = (
            "您好，我可以帮您查询订单、查看物流、咨询退款和售后规则。"
            "如果涉及高风险退款，我会先提交人工确认。"
        )

    return {
        "draft_answer": answer,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["general_answer：普通回答完成"],
    }


async def transfer_human_node(state: EcommerceAgentState) -> dict:
    result = await mock_transfer_human(
        reason=state["user_question"],
    )

    answer = f"我已经为您转接人工客服，工单号：{result['ticket_id']}。"

    return {
        "action_result": result,
        "draft_answer": answer,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["transfer_human：已创建人工客服工单"],
    }


def build_policy_query_node(state: EcommerceAgentState) -> dict:
    if state["intent"] == "after_sales":
        query = state["user_question"]
    elif state["order_info"] and state["order_info"].get("status") == "paid":
        query = "订单未发货退款规则"
    elif state["order_info"] and state["order_info"].get("status") == "shipped":
        query = "订单已发货退货退款规则"
    else:
        query = "售后规则"

    return {
        "policy_query": query,
        "logs": [f"build_policy_query：policy_query={query}"],
    }


async def retrieve_policy_node(state: EcommerceAgentState) -> dict:
    result = await mock_retrieve_policy(
        query=state["policy_query"],
    )

    return {
        "rag_hit": result["hit"],
        "policy_answer": result["answer"],
        "sources": result["sources"],
        "logs": [f"retrieve_policy：rag_hit={result['hit']}"],
    }


def route_after_policy(
    state: EcommerceAgentState,
) -> Literal["answer_policy", "assess_risk", "policy_fallback"]:
    if not state["rag_hit"] or not state["sources"]:
        return "policy_fallback"

    if state["intent"] == "refund":
        return "assess_risk"

    return "answer_policy"


def answer_policy_node(state: EcommerceAgentState) -> dict:
    answer = (
        f"{state['policy_answer']}"
        " 回答依据来自售后规则知识库。"
    )

    return {
        "draft_answer": answer,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["answer_policy：售后规则回答完成"],
    }


def policy_fallback_node(state: EcommerceAgentState) -> dict:
    answer = "根据当前知识库无法确认，建议联系人工客服进一步处理。"

    return {
        "draft_answer": answer,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["policy_fallback：知识库未命中"],
    }


def extract_order_id_node(state: EcommerceAgentState) -> dict:
    order_id = extract_order_id_from_text(
        state["user_question"]
    )

    if not order_id:
        order_id = state.get("order_id")

    return {
        "order_id": order_id,
        "logs": [f"extract_order_id：order_id={order_id}"],
    }


def route_after_extract_order_id(
    state: EcommerceAgentState,
) -> Literal["ask_order_id", "query_order"]:
    if not state["order_id"]:
        return "ask_order_id"

    return "query_order"


def ask_order_id_node(state: EcommerceAgentState) -> dict:
    if state["intent"] == "refund":
        answer = "请您提供订单号，我才能继续判断退款规则。"
    elif state["intent"] == "logistics":
        answer = "请您提供订单号，我才能继续查询物流。"
    else:
        answer = "请您提供订单号，我才能继续查询订单状态。"

    return {
        "draft_answer": answer,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["ask_order_id：缺少订单号，追问用户"],
    }


async def query_order_node(state: EcommerceAgentState) -> dict:
    result = await mock_query_order(
        order_id=state["order_id"],
    )

    if not result["success"]:
        return {
            "order_info": result.get("data"),
            "errors": [result["error"]],
            "logs": [f"query_order：失败 {result['error']}"],
        }

    return {
        "order_info": result["data"],
        "logs": [f"query_order：成功 {result['data']['status_text']}"],
    }


def route_after_query_order(
    state: EcommerceAgentState,
) -> Literal[
    "order_not_found",
    "logistics",
    "need_policy",
    "answer_order",
]:
    if state["errors"] and "order_not_found" in state["errors"]:
        return "order_not_found"

    if state["intent"] == "logistics":
        return "logistics"

    if state["intent"] == "refund":
        return "need_policy"

    return "answer_order"


def order_not_found_node(state: EcommerceAgentState) -> dict:
    answer = "没有查询到该订单，请您检查订单号是否正确。"

    return {
        "draft_answer": answer,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["order_not_found：订单不存在"],
    }


async def query_logistics_node(state: EcommerceAgentState) -> dict:
    result = await mock_query_logistics(
        order_info=state["order_info"],
    )

    if not result["success"]:
        answer = result["message"]
    else:
        data = result["data"]
        answer = (
            f"物流公司：{data['tracking_company']}，"
            f"物流单号：{data['tracking_no']}，"
            f"最新节点：{data['latest_event']}"
        )

    return {
        "draft_answer": answer,
        "logs": ["query_logistics：物流查询完成"],
    }


def answer_order_node(state: EcommerceAgentState) -> dict:
    order_info = state["order_info"]

    answer = f"您的订单当前状态是：{order_info['status_text']}。"

    if order_info.get("tracking_no"):
        answer += (
            f"物流公司：{order_info['tracking_company']}，"
            f"物流单号：{order_info['tracking_no']}，"
            f"最新节点：{order_info['latest_event']}。"
        )

    return {
        "draft_answer": answer,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["answer_order：订单回答完成"],
    }


def assess_risk_node(state: EcommerceAgentState) -> dict:
    order_info = state["order_info"] or {}
    amount = float(order_info.get("amount", 0))
    status = order_info.get("status")

    pending_payload = {
        "order_id": order_info.get("order_id"),
        "amount": amount,
        "currency": order_info.get("currency", "CNY"),
        "reason": "用户申请退款",
    }

    if status != "paid":
        return {
            "risk_level": "high",
            "need_human_confirm": True,
            "pending_action": "refund_order",
            "pending_payload": pending_payload,
            "logs": ["assess_risk：非待发货订单退款，高风险"],
        }

    if amount >= 500:
        return {
            "risk_level": "high",
            "need_human_confirm": True,
            "pending_action": "refund_order",
            "pending_payload": pending_payload,
            "logs": ["assess_risk：大额退款，高风险"],
        }

    return {
        "risk_level": "low",
        "need_human_confirm": False,
        "pending_action": "refund_order",
        "pending_payload": pending_payload,
        "logs": ["assess_risk：低风险，可自动给出退款建议"],
    }


def route_after_risk(
    state: EcommerceAgentState,
) -> Literal["human_review", "generate_refund_answer"]:
    if state["need_human_confirm"]:
        return "human_review"

    return "generate_refund_answer"


def human_review_node(state: EcommerceAgentState) -> dict:
    decision = interrupt({
        "type": "refund_review",
        "risk_level": state["risk_level"],
        "pending_action": state["pending_action"],
        "pending_payload": state["pending_payload"],
        "order_info": state["order_info"],
        "policy_answer": state["policy_answer"],
        "options": ["approve", "reject", "edit"],
        "message": "该退款请求需要人工审核，请确认是否继续处理。",
    })

    return {
        "human_decision": decision,
        "logs": [f"human_review：收到人工决策 {decision}"],
    }


def route_after_human_review(
    state: EcommerceAgentState,
) -> Literal["execute_refund", "reject_refund", "apply_edit"]:
    decision = state["human_decision"] or {}
    decision_type = decision.get("type")

    if decision_type == "approve":
        return "execute_refund"

    if decision_type == "edit":
        return "apply_edit"

    return "reject_refund"


def apply_edit_node(state: EcommerceAgentState) -> dict:
    decision = state["human_decision"] or {}
    edited_payload = decision.get("edited_payload") or {}

    return {
        "pending_payload": edited_payload,
        "logs": [f"apply_edit：人工修改退款参数 {edited_payload}"],
    }


async def execute_refund_node(state: EcommerceAgentState) -> dict:
    payload = state["pending_payload"] or {}

    result = await mock_execute_refund(payload)

    return {
        "action_result": result,
        "logs": [f"execute_refund：退款执行结果 {result}"],
    }


def reject_refund_node(state: EcommerceAgentState) -> dict:
    decision = state["human_decision"] or {}

    result = {
        "success": False,
        "reason": decision.get("reason", "人工拒绝退款"),
    }

    return {
        "action_result": result,
        "logs": [f"reject_refund：人工拒绝 {result}"],
    }


def generate_refund_answer_node(state: EcommerceAgentState) -> dict:
    order_info = state["order_info"] or {}
    policy_answer = state["policy_answer"] or ""
    action_result = state["action_result"]

    if action_result:
        if action_result.get("success"):
            payload = action_result.get("executed_payload") or {}
            answer = (
                f"退款已提交处理。订单号：{payload.get('order_id')}，"
                f"退款金额：{payload.get('amount')} {payload.get('currency')}。"
            )
        else:
            answer = (
                "本次退款暂未执行。"
                f"原因：{action_result.get('reason', '未说明')}。"
            )
    else:
        answer = (
            f"结论：您的订单当前可以按规则申请退款。\n\n"
            f"订单状态：{order_info.get('status_text')}。"
            f"{policy_answer}"
        )

    return {
        "draft_answer": answer,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["generate_refund_answer：退款回答生成完成"],
    }


def review_answer_node(state: EcommerceAgentState) -> dict:
    answer = state["draft_answer"]

    risky_words = [
        "保证退款",
        "一定退款",
        "立即到账",
        "百分百成功",
    ]

    has_risky_word = any(word in answer for word in risky_words)

    if has_risky_word and state["retry_count"] < state["max_retry"]:
        return {
            "errors": ["answer_has_risky_promise"],
            "logs": ["review_answer：回答包含过度承诺，需要改写"],
        }

    return {
        "logs": ["review_answer：回答审核通过"],
    }


def route_after_review(
    state: EcommerceAgentState,
) -> Literal["rewrite", "finish"]:
    if state["errors"] and "answer_has_risky_promise" in state["errors"]:
        if state["retry_count"] < state["max_retry"]:
            return "rewrite"

    return "finish"


def rewrite_answer_node(state: EcommerceAgentState) -> dict:
    rewritten = (
        state["draft_answer"]
        .replace("保证退款", "可按规则申请退款")
        .replace("一定退款", "通常可按规则处理")
        .replace("立即到账", "以实际到账时间为准")
        .replace("百分百成功", "以平台审核结果为准")
    )

    return {
        "draft_answer": rewritten,
        "retry_count": state["retry_count"] + 1,
        "logs": ["rewrite_answer：已移除过度承诺表达"],
    }


def finish_node(state: EcommerceAgentState) -> dict:
    answer = state["draft_answer"]

    return {
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "agent_trace": [
            {
                "node_name": "finish",
                "input_summary": "draft_answer",
                "output_summary": answer[:100],
                "route_to": None,
                "reason": "客服回答最终输出",
            }
        ],
        "logs": ["finish：流程结束"],
    }


def build_ecommerce_agent_graph(
    checkpointer=None,
    store=None,
):
    graph = StateGraph(
        EcommerceAgentState,
        context_schema=EcommerceAgentContext,
    )

    graph.add_node("recall_memory", recall_memory_node)
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("write_memory", write_memory_node)
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
    graph.add_node("query_logistics", query_logistics_node)
    graph.add_node("answer_order", answer_order_node)

    graph.add_node("assess_risk", assess_risk_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("apply_edit", apply_edit_node)
    graph.add_node("execute_refund", execute_refund_node)
    graph.add_node("reject_refund", reject_refund_node)
    graph.add_node("generate_refund_answer", generate_refund_answer_node)

    graph.add_node("review_answer", review_answer_node)
    graph.add_node("rewrite_answer", rewrite_answer_node)
    graph.add_node("finish", finish_node)

    graph.add_edge(START, "recall_memory")
    graph.add_edge("recall_memory", "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "remember": "write_memory",
            "general": "general_answer",
            "human": "transfer_human",
            "policy_only": "build_policy_query",
            "need_order": "extract_order_id",
        },
    )

    graph.add_edge("build_policy_query", "retrieve_policy")

    graph.add_conditional_edges(
        "retrieve_policy",
        route_after_policy,
        {
            "answer_policy": "answer_policy",
            "assess_risk": "assess_risk",
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
            "logistics": "query_logistics",
            "need_policy": "build_policy_query",
            "answer_order": "answer_order",
        },
    )

    graph.add_conditional_edges(
        "assess_risk",
        route_after_risk,
        {
            "human_review": "human_review",
            "generate_refund_answer": "generate_refund_answer",
        },
    )

    graph.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "execute_refund": "execute_refund",
            "reject_refund": "reject_refund",
            "apply_edit": "apply_edit",
        },
    )

    graph.add_edge("apply_edit", "execute_refund")
    graph.add_edge("execute_refund", "generate_refund_answer")
    graph.add_edge("reject_refund", "generate_refund_answer")

    graph.add_edge("general_answer", "review_answer")
    graph.add_edge("transfer_human", "review_answer")
    graph.add_edge("answer_policy", "review_answer")
    graph.add_edge("policy_fallback", "review_answer")
    graph.add_edge("ask_order_id", "review_answer")
    graph.add_edge("order_not_found", "review_answer")
    graph.add_edge("query_logistics", "review_answer")
    graph.add_edge("answer_order", "review_answer")
    graph.add_edge("generate_refund_answer", "review_answer")

    graph.add_conditional_edges(
        "review_answer",
        route_after_review,
        {
            "rewrite": "rewrite_answer",
            "finish": "finish",
        },
    )

    graph.add_edge("rewrite_answer", "review_answer")
    graph.add_edge("write_memory", END)
    graph.add_edge("finish", END)

    if checkpointer is None:
        checkpointer = InMemorySaver()

    if store is None:
        store = InMemoryStore()

    app = graph.compile(
        checkpointer=checkpointer,
        store=store,
    )

    return app, store