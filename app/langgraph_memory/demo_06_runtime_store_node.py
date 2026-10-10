from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime


from app.langgraph_memory.schemas import (
    MemoryContext,
    MemoryState,
    create_initial_memory_state,
)


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

    recalled_memories = []

    for item in items:
        value = item.value
        recalled_memories.append({
            "key": item.key,
            "type": value.get("type", "preference"),
            "content": value.get("content", ""),
            "confidence": value.get("confidence", 0.8),
            "source": value.get("source", "store"),
        })

    return {
        "recalled_memories": recalled_memories,
        "logs": [f"recall_memory：召回 {len(recalled_memories)} 条长期记忆"],
    }


def answer_node(state: MemoryState) -> dict:
    if state["recalled_memories"]:
        memory_text = "\n".join(
            f"- {item['content']}"
            for item in state["recalled_memories"]
        )
    else:
        memory_text = "暂无长期记忆"

    answer = (
        "我会结合你的长期偏好回答。\n\n"
        f"【召回记忆】\n{memory_text}"
    )

    return {
        "messages": [
            AIMessage(content=answer)
        ],
        "final_answer": answer,
        "is_finished": True,
        "logs": ["answer：基于长期记忆生成回答"],
    }


def build_graph():
    graph = StateGraph(MemoryState,context_schema=MemoryContext)

    graph.add_node("recall_memory", recall_memory_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "recall_memory")
    graph.add_edge("recall_memory", "answer")
    graph.add_edge("answer", END)

    store = InMemoryStore()
    checkpointer = InMemorySaver()

    return graph.compile(
        store=store,
        checkpointer=checkpointer,
    )


def main():
    app = build_graph()

    tenant_id = "tenant_001"
    user_id = "u_10001"

    namespace = (tenant_id, user_id, "preferences")

    app.store.put(
        namespace,
        "answer_style",
        {
            "type": "preference",
            "content": "用户喜欢口语化、不要太官方的回答。",
            "confidence": 0.95,
            "source": "manual_seed",
        },
    )

    result = app.invoke(
        create_initial_memory_state("你应该怎么回答我？"),
        config={
            "configurable": {
                "thread_id": "thread_runtime_store_demo"
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