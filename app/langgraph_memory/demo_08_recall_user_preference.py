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


def recall_preference_node(
    state: MemoryState,
    runtime: Runtime[MemoryContext],
) -> dict:
    namespace = (
        runtime.context.tenant_id,
        runtime.context.user_id,
        "preferences",
    )

    items = runtime.store.search(namespace)

    recalled = []

    for item in items:
        value = item.value
        recalled.append({
            "key": item.key,
            "type": value.get("type", "preference"),
            "content": value.get("content", ""),
            "confidence": value.get("confidence", 0.8),
            "source": value.get("source", "store"),
        })

    return {
        "recalled_memories": recalled,
        "logs": [f"recall_preference：召回 {len(recalled)} 条偏好"],
    }


def answer_with_preference_node(state: MemoryState) -> dict:
    if not state["recalled_memories"]:
        answer = "我还没有记录到你的长期偏好。"
    else:
        preference_text = "\n".join(
            f"- {memory['content']}"
            for memory in state["recalled_memories"]
        )

        answer = (
            "我记得你的这些偏好：\n"
            f"{preference_text}\n\n"
            "后续回答我会尽量按这些要求来。"
        )

    return {
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["answer_with_preference：回答完成"],
    }


def build_graph():
    graph = StateGraph(
        MemoryState,
        context_schema=MemoryContext,
    )

    graph.add_node("recall_preference", recall_preference_node)
    graph.add_node("answer_with_preference", answer_with_preference_node)

    graph.add_edge(START, "recall_preference")
    graph.add_edge("recall_preference", "answer_with_preference")
    graph.add_edge("answer_with_preference", END)

    store = InMemoryStore()
    checkpointer = InMemorySaver()

    app = graph.compile(
        store=store,
        checkpointer=checkpointer,
    )

    return app, store


def main():
    app, store = build_graph()

    tenant_id = "tenant_001"
    user_id = "u_10001"
    namespace = (tenant_id, user_id, "preferences")

    store.put(
        namespace,
        "answer_style",
        {
            "type": "preference",
            "content": "回答要口语化，不要太像官方文档。",
            "confidence": 0.95,
            "source": "manual_seed",
        },
    )

    store.put(
        namespace,
        "code_style",
        {
            "type": "preference",
            "content": "涉及代码时，要给完整可运行示例。",
            "confidence": 0.95,
            "source": "manual_seed",
        },
    )

    result = app.invoke(
        create_initial_memory_state("你记得我的偏好吗？"),
        config={
            "configurable": {
                "thread_id": "thread_recall_preference_demo"
            }
        },
        context=MemoryContext(
            tenant_id=tenant_id,
            user_id=user_id,
        ),
    )

    print(result["final_answer"])
    print("=" * 80)
    print("logs:")
    for log in result["logs"]:
        print("-", log)


if __name__ == "__main__":
    main()