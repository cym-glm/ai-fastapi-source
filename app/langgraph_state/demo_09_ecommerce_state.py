from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from app.langgraph_state.schemas import EcommerceAgentState


def create_initial_ecommerce_state(
    user_question: str,
) -> EcommerceAgentState:
    return {
        "user_question": user_question,
        "messages": [HumanMessage(content=user_question)],

        "intent": "unknown",
        "order_id": None,
        "tracking_no": None,

        "order_info": None,
        "logistics_info": None,

        "policy_query": None,
        "policy_answer": None,
        "sources": [],

        "risk_level": "low",
        "need_human_confirm": False,
        "pending_action": None,

        "tool_calls": [],
        "logs": [],
        "errors": [],

        "final_answer": "",
        "is_finished": False,
    }


def classify_intent_node(state: EcommerceAgentState) -> dict:
    question = state["user_question"]

    if "退款" in question or "退货" in question:
        intent = "refund"
    elif "物流" in question:
        intent = "logistics"
    elif "订单" in question:
        intent = "query_order"
    elif "人工" in question:
        intent = "human_service"
    else:
        intent = "general"

    return {
        "intent": intent,
        "logs": [f"classify_intent：识别意图为 {intent}"],
    }


def extract_order_id_node(state: EcommerceAgentState) -> dict:
    question = state["user_question"]

    if "10001" in question:
        order_id = "10001"
    elif "10002" in question:
        order_id = "10002"
    else:
        order_id = None

    return {
        "order_id": order_id,
        "logs": [f"extract_order_id：订单号为 {order_id}"],
    }


def query_order_node(state: EcommerceAgentState) -> dict:
    order_id = state["order_id"]

    if order_id == "10001":
        order_info = {
            "order_id": "10001",
            "status": "shipped",
            "status_text": "已发货",
            "tracking_company": "顺丰",
            "tracking_no": "SF10001",
            "latest_event": "包裹已到达成都高新区中转站。",
        }
    elif order_id == "10002":
        order_info = {
            "order_id": "10002",
            "status": "paid",
            "status_text": "已付款，待发货",
            "tracking_company": None,
            "tracking_no": None,
            "latest_event": None,
        }
    else:
        order_info = {
            "order_id": order_id or "",
            "status": "not_found",
            "status_text": "未查询到订单",
            "tracking_company": None,
            "tracking_no": None,
            "latest_event": None,
        }

    return {
        "order_info": order_info,
        "tool_calls": [
            {
                "name": "query_order",
                "args": {"order_id": order_id},
                "id": "mock_query_order",
                "success": True,
                "result_preview": order_info["status_text"],
            }
        ],
        "logs": [f"query_order：订单状态为 {order_info['status_text']}"],
    }


def retrieve_policy_node(state: EcommerceAgentState) -> dict:
    order_info = state.get("order_info")

    if order_info and order_info.get("status") == "paid":
        policy_answer = "订单未发货时，用户可以申请取消订单并退款。"
        policy_query = "订单未发货退款规则"
    elif order_info and order_info.get("status") == "shipped":
        policy_answer = "订单已发货后，需要用户收到商品后再发起退货退款申请。"
        policy_query = "订单已发货退货退款规则"
    else:
        policy_answer = "当前状态无法确认退款规则，建议转人工客服。"
        policy_query = "退款规则"

    return {
        "policy_query": policy_query,
        "policy_answer": policy_answer,
        "sources": [
            {
                "document_id": "ecommerce_after_sales",
                "chunk_id": "ecommerce_after_sales_chunk_0",
                "source": "data/knowledge_base/ecommerce_after_sales.md",
                "content_preview": policy_answer,
                "score": 0.9,
            }
        ],
        "logs": ["retrieve_policy：完成售后规则查询"],
    }


def generate_answer_node(state: EcommerceAgentState) -> dict:
    order_info = state.get("order_info")
    policy_answer = state.get("policy_answer")

    if state["intent"] == "refund":
        answer = (
            f"您的订单当前状态是：{order_info['status_text']}。"
            f"{policy_answer}"
        )
    elif state["intent"] == "query_order":
        answer = f"您的订单当前状态是：{order_info['status_text']}。"
    else:
        answer = "这是普通问题，可以走普通 Chat。"

    return {
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["generate_answer：最终回答生成完成"],
    }


def build_graph():
    graph = StateGraph(EcommerceAgentState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("query_order", query_order_node)
    graph.add_node("retrieve_policy", retrieve_policy_node)
    graph.add_node("generate_answer", generate_answer_node)

    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "extract_order_id")
    graph.add_edge("extract_order_id", "query_order")
    graph.add_edge("query_order", "retrieve_policy")
    graph.add_edge("retrieve_policy", "generate_answer")
    graph.add_edge("generate_answer", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke(
        create_initial_ecommerce_state(
            "我的订单 10002 还没发货，可以退款吗？"
        )
    )

    print("final_answer:")
    print(result["final_answer"])

    print("=" * 80)
    print("sources:")
    for source in result["sources"]:
        print(source)

    print("=" * 80)
    print("tool_calls:")
    for tool_call in result["tool_calls"]:
        print(tool_call)

    print("=" * 80)
    print("logs:")
    for log in result["logs"]:
        print("-", log)

    print("=" * 80)
    print("messages:")
    for message in result["messages"]:
        print(message.type, ":", message.content)


if __name__ == "__main__":
    main()