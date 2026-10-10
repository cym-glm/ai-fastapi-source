import uuid
from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore

from app.langgraph_memory.schemas import (
    MemoryContext,
    MemoryState,
    create_initial_memory_state,
)


def classify_intent_node(state: MemoryState) -> dict:
    question = state["user_question"]

    if "记住" in question or "以后" in question:
        intent = "remember_preference"
    elif "我的偏好" in question or "你记得" in question:
        intent = "recall_preference"
    elif "订单" in question or "退款" in question or "物流" in question:
        intent = "ecommerce_service"
    else:
        intent = "general"

    return {
        "intent": intent,
        "logs": [f"classify_intent：intent={intent}"],
    }


def route_by_intent(
    state: MemoryState,
) -> Literal["remember", "recall", "service", "general"]:
    if state["intent"] == "remember_preference":
        return "remember"

    if state["intent"] == "recall_preference":
        return "recall"

    if state["intent"] == "ecommerce_service":
        return "service"

    return "general"


def write_memory_node(
    state: MemoryState,
    runtime: Runtime[MemoryContext],
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

    runtime.store.put(namespace, key, memory)

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
        "logs": [f"write_memory：写入偏好 key={key}"],
    }


def recall_memory_node(
    state: MemoryState,
    runtime: Runtime[MemoryContext],
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
        "logs": [f"recall_memory：召回 {len(memories)} 条记忆"],
    }


def answer_recall_node(state: MemoryState) -> dict:
    if not state["recalled_memories"]:
        answer = "我现在还没有记录到你的长期偏好。"
    else:
        text = "\n".join(
            f"- {memory['content']}"
            for memory in state["recalled_memories"]
        )
        answer = f"我记得你的偏好：\n{text}"

    return {
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["answer_recall：回答偏好记忆"],
    }


def ecommerce_service_node(state: MemoryState) -> dict:
    preference_text = "\n".join(
        memory["content"]
        for memory in state["recalled_memories"]
    )

    if preference_text:
        answer = (
            "我会结合你的偏好来回答。\n"
            f"你的偏好：{preference_text}\n\n"
            "针对电商客服问题：我会先给结论，再补充处理建议。"
        )
    else:
        answer = (
            "这是电商客服问题。"
            "我会先判断订单、退款或物流场景，再给处理建议。"
        )

    return {
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["ecommerce_service：结合记忆完成客服回答"],
    }


def general_answer_node(state: MemoryState) -> dict:
    answer = "这是普通问题，可以走普通 ChatModel。"

    return {
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["general_answer：普通回答"],
    }


def build_graph():
    graph = StateGraph(
        MemoryState,
        context_schema=MemoryContext,
    )

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("write_memory", write_memory_node)
    graph.add_node("recall_memory", recall_memory_node)
    graph.add_node("answer_recall", answer_recall_node)
    graph.add_node("ecommerce_service", ecommerce_service_node)
    graph.add_node("general_answer", general_answer_node)

    graph.add_edge(START, "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "remember": "write_memory",
            "recall": "recall_memory",
            "service": "recall_memory",
            "general": "general_answer",
        },
    )

    graph.add_conditional_edges(
        "recall_memory",
        lambda state: "answer_recall" if state["intent"] == "recall_preference" else "service",
        {
            "answer_recall": "answer_recall",
            "service": "ecommerce_service",
        },
    )

    graph.add_edge("write_memory", END)
    graph.add_edge("answer_recall", END)
    graph.add_edge("ecommerce_service", END)
    graph.add_edge("general_answer", END)

    store = InMemoryStore()
    checkpointer = InMemorySaver()

    app = graph.compile(
        store=store,
        checkpointer=checkpointer,
    )

    return app, store


def main():
    app, store = build_graph()

    context = MemoryContext(
        tenant_id="tenant_001",
        user_id="u_10001",
    )

    config = {
        "configurable": {
            "thread_id": "thread_ecommerce_memory_demo"
        }
    }

    first = app.invoke(
        create_initial_memory_state(
            "记住：以后回答客服问题，先给结论，再给处理步骤。"
        ),
        config=config,
        context=context,
    )

    print("first:")
    print(first["final_answer"])
    print("=" * 80)

    second = app.invoke(
        create_initial_memory_state(
            "你记得我的偏好吗？"
        ),
        config=config,
        context=context,
    )

    print("second:")
    print(second["final_answer"])
    print("=" * 80)

    third = app.invoke(
        create_initial_memory_state(
            "我的订单 10002 可以退款吗？"
        ),
        config=config,
        context=context,
    )

    print("third:")
    print(third["final_answer"])
    print("=" * 80)

    print("logs:")
    for log in third["logs"]:
        print("-", log)


if __name__ == "__main__":
    main()