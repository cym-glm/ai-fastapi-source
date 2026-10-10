from app.langgraph_persistence.graph_factory import (
    add_user_message_to_state,
    build_memory_graph,
)
from app.langgraph_persistence.schemas import create_initial_state


class LangGraphPersistenceService:
    def __init__(self):
        # 教学版使用内存 checkpointer。
        # 生产环境应该替换成 PostgresSaver / AsyncPostgresSaver。
        self.graph = build_memory_graph()

    def build_thread_id(
        self,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
    ) -> str:
        return f"{tenant_id}:{user_id}:{conversation_id}"

    def build_config(
        self,
        thread_id: str,
    ) -> dict:
        return {
            "configurable": {
                "thread_id": thread_id
            }
        }

    def start_refund_flow(
        self,
        user_question: str,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
    ) -> dict:
        thread_id = self.build_thread_id(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        config = self.build_config(thread_id)

        return self.graph.invoke(
            create_initial_state(user_question),
            config=config,
        )

    def continue_flow(
        self,
        user_question: str,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
    ) -> dict:
        thread_id = self.build_thread_id(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        config = self.build_config(thread_id)

        return self.graph.invoke(
            add_user_message_to_state(user_question),
            config=config,
        )

    def get_current_state(
        self,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
    ) -> dict:
        thread_id = self.build_thread_id(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        config = self.build_config(thread_id)

        snapshot = self.graph.get_state(config)

        return {
            "thread_id": thread_id,
            "values": snapshot.values,
            "next": snapshot.next,
            "config": snapshot.config,
        }


langgraph_persistence_service = LangGraphPersistenceService()