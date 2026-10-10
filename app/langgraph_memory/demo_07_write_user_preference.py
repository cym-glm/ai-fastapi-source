import uuid

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


def classify_memory_intent_node(state: MemoryState) -> dict:
    question = state["user_question"]

    if "记住" in question or "以后回答" in question or "以后你" in question:
        intent = "remember_preference"
    elif "你记得" in question or "我的偏好" in question:
        intent = "recall_preference"
    else:
        intent = "general"

    return {
        "intent": intent,
        "logs": [f"classify_memory_intent：intent={intent}"],
    }


def write_preference_node(
    state: MemoryState,
    runtime: Runtime[MemoryContext],
) -> dict:
    namespace = (
        runtime.context.tenant_id,
        runtime.context.user_id,
        "preferences",
    )

    content = state["user_question"]

    memory = {
        "type": "preference",
        "content": content,
        "confidence": 0.85,
        "source": "user_explicit_request",
    }

    memory_key = f"pref_{uuid.uuid4().hex}"

    runtime.store.put(
        namespace,
        memory_key,
        memory,
    )

    return {
        "new_memories": [
            {
                "key": memory_key,
                **memory,
            }
        ],
        "final_answer": "好的，我已经记住你的这个偏好。",
        "is_finished": True,
        "messages": [
            AIMessage(content="好的，我已经记住你的这个偏好。")
        ],
        "logs": [f"write_preference：写入记忆 key={memory_key}"],
    }


def build_graph():
    graph = StateGraph(
        MemoryState,
        context_schema=MemoryContext,
    )

    graph.add_node("classify_memory_intent", classify_memory_intent_node)
    graph.add_node("write_preference", write_preference_node)

    graph.add_edge(START, "classify_memory_intent")
    graph.add_edge("classify_memory_intent", "write_preference")
    graph.add_edge("write_preference", END)

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

    result = app.invoke(
        create_initial_memory_state(
            "记住：以后回答面试题，要给我口语化话术和代码示例。"
        ),
        config={
            "configurable": {
                "thread_id": "thread_write_preference_demo"
            }
        },
        context=MemoryContext(
            tenant_id=tenant_id,
            user_id=user_id,
        ),
    )

    print("final_answer:", result["final_answer"])
    print("new_memories:", result["new_memories"])

    print("=" * 80)

    namespace = (tenant_id, user_id, "preferences")
    items = store.search(namespace)

    print("store memories:")
    for item in items:
        print(item.key, item.value)


if __name__ == "__main__":
    main()