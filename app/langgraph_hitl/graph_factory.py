from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.langgraph_hitl.schemas import HITLState


def classify_intent_node(state: HITLState) -> dict:
    question = state.get("user_question") or ""

    if "退款" in question or "退货" in question:
        intent = "refund"
    elif "订单" in question:
        intent = "query_order"
    elif "人工" in question:
        intent = "human_service"
    else:
        intent = "general"

    return {
        "intent": intent,
        "logs": [f"classify_intent：intent={intent}"],
    }


def route_by_intent(
    state: HITLState,
) -> Literal["refund", "general"]:
    if state["intent"] == "refund":
        return "refund"

    return "general"


def general_answer_node(state: HITLState) -> dict:
    answer = "这是普通问题，可以走普通 ChatModel。"

    return {
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["general_answer：普通回答完成"],
    }


def extract_order_id_node(state: HITLState) -> dict:
    question = state["user_question"]

    if "10001" in question:
        order_id = "10001"
    elif "10002" in question:
        order_id = "10002"
    elif "10003" in question:
        order_id = "10003"
    else:
        order_id = None

    return {
        "order_id": order_id,
        "logs": [f"extract_order_id：order_id={order_id}"],
    }


def route_after_extract_order_id(
    state: HITLState,
) -> Literal["ask_order_id", "query_order"]:
    if not state["order_id"]:
        return "ask_order_id"

    return "query_order"


def ask_order_id_node(state: HITLState) -> dict:
    answer = "请您提供订单号，我才能继续处理退款申请。"

    return {
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["ask_order_id：缺少订单号"],
    }


def query_order_node(state: HITLState) -> dict:
    order_id = state["order_id"]

    if order_id == "10001":
        order_info = {
            "order_id": "10001",
            "status": "shipped",
            "status_text": "已发货",
            "amount": 399.0,
            "currency": "CNY",
        }
    elif order_id == "10002":
        order_info = {
            "order_id": "10002",
            "status": "paid",
            "status_text": "已付款，待发货",
            "amount": 199.0,
            "currency": "CNY",
        }
    elif order_id == "10003":
        order_info = {
            "order_id": "10003",
            "status": "paid",
            "status_text": "已付款，待发货",
            "amount": 1299.0,
            "currency": "CNY",
        }
    else:
        order_info = {
            "order_id": order_id or "",
            "status": "not_found",
            "status_text": "未查询到订单",
            "amount": 0.0,
            "currency": "CNY",
        }

    return {
        "order_info": order_info,
        "logs": [f"query_order：{order_info['status_text']}"],
    }


def route_after_query_order(
    state: HITLState,
) -> Literal["order_not_found", "prepare_refund"]:
    order_info = state["order_info"]

    if not order_info or order_info["status"] == "not_found":
        return "order_not_found"

    return "prepare_refund"


def order_not_found_node(state: HITLState) -> dict:
    answer = "没有查询到该订单，请您检查订单号是否正确。"

    return {
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["order_not_found：订单不存在"],
    }


def prepare_refund_node(state: HITLState) -> dict:
    order_info = state["order_info"]

    refund_amount = float(order_info["amount"])

    if order_info["status"] == "paid":
        refund_reason = "订单未发货，用户申请取消订单并退款。"
    elif order_info["status"] == "shipped":
        refund_reason = "订单已发货，需要人工确认是否允许直接退款。"
    else:
        refund_reason = "订单状态异常，需要人工确认。"

    pending_payload = {
        "order_id": order_info["order_id"],
        "amount": refund_amount,
        "currency": order_info["currency"],
        "reason": refund_reason,
    }

    return {
        "refund_amount": refund_amount,
        "refund_reason": refund_reason,
        "pending_action": "refund_order",
        "pending_payload": pending_payload,
        "logs": [f"prepare_refund：pending_payload={pending_payload}"],
    }


def assess_risk_node(state: HITLState) -> dict:
    order_info = state["order_info"]
    refund_amount = state["refund_amount"] or 0

    if order_info["status"] != "paid":
        return {
            "risk_level": "high",
            "need_human_confirm": True,
            "logs": ["assess_risk：非待发货订单退款，高风险"],
        }

    if refund_amount >= 500:
        return {
            "risk_level": "high",
            "need_human_confirm": True,
            "logs": ["assess_risk：大额退款，高风险"],
        }

    return {
        "risk_level": "low",
        "need_human_confirm": False,
        "logs": ["assess_risk：低风险，可自动退款"],
    }


def route_after_risk(
    state: HITLState,
) -> Literal["human_review", "execute_refund"]:
    if state["need_human_confirm"]:
        return "human_review"

    return "execute_refund"


def human_review_node(state: HITLState) -> dict:

    decision = interrupt({
        "type": "refund_review",
        "risk_level": state["risk_level"],
        "pending_action": state["pending_action"],
        "pending_payload": state["pending_payload"],
        "order_info": state["order_info"],
        "options": ["approve", "reject", "edit"],
        "message": "该退款请求需要人工审核，请确认是否继续执行。",
    })
    

    return {
        "human_decision": decision,
        "logs": [f"human_review：收到人工决策 {decision}"],
    }


def route_after_human_review(
    state: HITLState,
) -> Literal["execute_refund", "reject_refund", "apply_edit"]:
    decision = state["human_decision"] or {}
    decision_type = decision.get("type")

    if decision_type == "approve":
        return "execute_refund"

    if decision_type == "edit":
        return "apply_edit"

    return "reject_refund"


def apply_edit_node(state: HITLState) -> dict:
    decision = state["human_decision"] or {}
    edited_payload = decision.get("edited_payload") or {}

    return {
        "pending_payload": edited_payload,
        "refund_amount": float(edited_payload.get("amount", 0)),
        "logs": [f"apply_edit：人工修改退款参数 {edited_payload}"],
    }


def execute_refund_node(state: HITLState) -> dict:
    payload = state["pending_payload"] or {}

    # 教学版：这里不调用真实支付或订单系统，只模拟执行。
    # 生产环境：这里才是真正调用退款工具的位置。
    action_result = {
        "success": True,
        "refund_id": f"rf_{payload.get('order_id', 'unknown')}",
        "executed_payload": payload,
    }

    return {
        "action_result": action_result,
        "logs": [f"execute_refund：退款执行成功 {action_result}"],
    }


def reject_refund_node(state: HITLState) -> dict:
    decision = state["human_decision"] or {}

    action_result = {
        "success": False,
        "reason": decision.get("reason", "人工拒绝退款"),
    }

    return {
        "action_result": action_result,
        "logs": [f"reject_refund：人工拒绝 {action_result}"],
    }


def generate_answer_node(state: HITLState) -> dict:
    action_result = state["action_result"] or {}

    if action_result.get("success"):
        payload = action_result.get("executed_payload") or {}
        answer = (
            f"退款已处理成功。订单号：{payload.get('order_id')}，"
            f"退款金额：{payload.get('amount')} {payload.get('currency')}。"
        )
    else:
        answer = (
            "本次退款暂未执行。"
            f"原因：{action_result.get('reason', '未说明')}。"
        )

    return {
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["generate_answer：最终回答完成"],
    }


def build_hitl_refund_graph(
    checkpointer=None,
):
    graph = StateGraph(HITLState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("general_answer", general_answer_node)
    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("ask_order_id", ask_order_id_node)
    graph.add_node("query_order", query_order_node)
    graph.add_node("order_not_found", order_not_found_node)
    graph.add_node("prepare_refund", prepare_refund_node)
    graph.add_node("assess_risk", assess_risk_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("apply_edit", apply_edit_node)
    graph.add_node("execute_refund", execute_refund_node)
    graph.add_node("reject_refund", reject_refund_node)
    graph.add_node("generate_answer", generate_answer_node)

    graph.add_edge(START, "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "refund": "extract_order_id",
            "general": "general_answer",
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
            "prepare_refund": "prepare_refund",
        },
    )

    graph.add_edge("prepare_refund", "assess_risk")

    graph.add_conditional_edges(
        "assess_risk",
        route_after_risk,
        {
            "human_review": "human_review",
            "execute_refund": "execute_refund",
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
    graph.add_edge("execute_refund", "generate_answer")
    graph.add_edge("reject_refund", "generate_answer")

    graph.add_edge("general_answer", END)
    graph.add_edge("ask_order_id", END)
    graph.add_edge("order_not_found", END)
    graph.add_edge("generate_answer", END)

    return graph.compile(checkpointer=checkpointer)


def build_memory_hitl_graph():
    checkpointer = InMemorySaver()

    return build_hitl_refund_graph(
        checkpointer=checkpointer,
    )