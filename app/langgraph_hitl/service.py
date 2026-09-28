from langgraph.types import Command

from app.langgraph_hitl.graph_factory import build_memory_hitl_graph
from app.langgraph_hitl.schemas import create_initial_state


class LangGraphHITLService:
    def __init__(self):
        # 教学版用内存 checkpointer。
        # 生产环境替换成 AsyncPostgresSaver。
        self.graph = build_memory_hitl_graph()

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

    def start(
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

        result = self.graph.invoke(
            create_initial_state(user_question),
            config=config,
        )

        return {
            "thread_id": thread_id,
            "result": result,
        }

    def resume(
        self,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
        decision: dict,
    ) -> dict:
        thread_id = self.build_thread_id(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        config = self.build_config(thread_id)

        result = self.graph.invoke(
            Command(resume=decision),
            config=config,
        )

        return {
            "thread_id": thread_id,
            "result": result,
        }

    def get_state(
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


langgraph_hitl_service = LangGraphHITLService()