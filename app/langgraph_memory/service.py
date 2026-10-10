from app.langgraph_memory.demo_09_ecommerce_memory_graph import build_graph
from app.langgraph_memory.schemas import (
    MemoryContext,
    create_initial_memory_state,
)


class LangGraphMemoryService:
    def __init__(self):
        self.graph, self.store = build_graph()

    def build_thread_id(
        self,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
    ) -> str:
        return f"{tenant_id}:{user_id}:{conversation_id}"

    def chat(
        self,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
        question: str,
    ) -> dict:
        thread_id = self.build_thread_id(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        result = self.graph.invoke(
            create_initial_memory_state(question),
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            },
            context=MemoryContext(
                tenant_id=tenant_id,
                user_id=user_id,
            ),
        )

        return {
            "thread_id": thread_id,
            "answer": result["final_answer"],
            "intent": result["intent"],
            "recalled_memories": result["recalled_memories"],
            "new_memories": result["new_memories"],
            "logs": result["logs"],
        }

    def list_memories(
        self,
        tenant_id: str,
        user_id: str,
        memory_type: str = "preferences",
    ) -> list[dict]:
        namespace = (
            tenant_id,
            user_id,
            memory_type,
        )

        items = self.store.search(namespace)

        return [
            {
                "key": item.key,
                "value": item.value,
            }
            for item in items
        ]


langgraph_memory_service = LangGraphMemoryService()