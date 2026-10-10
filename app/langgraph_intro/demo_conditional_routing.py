


from typing import Literal, TypedDict

from langgraph.graph import StateGraph, END, START

class RouterState(TypedDict):
    user_question: str
    intent: str
    answer: str = ""

def classify_intent_node(state: RouterState) -> str:
    question = state["user_question"]

    if "退款" in question:
        intent = "refund"
    elif "订单" in question or "物流" in question:
        intent= "order"
    else:
        intent = "general"
    return {
        "intent": intent,
    }


def route_by_intent(
    state: RouterState,
)-> Literal["refund_answer", "order_answer", "general_answer"]:
    intent = state["intent"]
    if intent == "refund":
        return "refund_answer"
    if intent == "order":
        return "order_answer"
    
    return "general_answer" 

def general_answer_node(state: RouterState) -> dict:
    return {
        "answer": "这是通用回答， 走普通的chat",
    }

def order_answer_node(state: RouterState) -> dict:
    return {
        "answer": "这是订单回答， 下一步应该查询订单系统。",
    }

def refund_answer_node(state: RouterState) -> dict:
    return {
        "answer": "这是退款问题，下一步应该查询订单状态和退款规则",
    }


def build_graph():
    # 定义State  
    graph = StateGraph(RouterState)
    # 定义Node
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("general_answer", general_answer_node)
    graph.add_node("order_answer", order_answer_node)
    graph.add_node("refund_answer", refund_answer_node)
    # 定义Edge
    graph.add_edge(START, "classify_intent")
    # 添加条件 分支
    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "general_answer": "general_answer",
            "order_answer": "order_answer",
            "refund_answer": "refund_answer",
        }

    )
    graph.add_edge("general_answer", END)
    graph.add_edge("order_answer", END)
    graph.add_edge("refund_answer", END)

    # complie编译 ---- invoke
    return graph.compile()

def main():
    app = build_graph()

    questions = [
        "你好，介绍一下 LangGraph。",
        "帮我查一下订单 10001。",
        "我的订单还没发货，可以退款吗？",
    ]

    for question in questions:
        result = app.invoke({
            "user_question": question,
            "intent": "",
            "answer": "",
        })
        print(f"{question} ----> {result['answer']}")


if __name__ == "__main__":
    main()