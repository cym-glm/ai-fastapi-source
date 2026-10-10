from langgraph.types import Command

from app.langgraph_ecommerce_agent.graph_factory import build_ecommerce_agent_graph
from app.langgraph_ecommerce_agent.schemas import (
    EcommerceAgentContext,
    append_user_message,
    create_initial_state,
)


class LangGraphEcommerceAgentService:
    def __init__(self):
        self.graph, self.store = build_ecommerce_agent_graph()

    def build_thread_id(
        self,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
    ) -> str:
        return f"{tenant_id}:{user_id}:{conversation_id}"

    def build_context(
        self,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
    ) -> EcommerceAgentContext:
        return EcommerceAgentContext(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

    def build_config(
        self,
        thread_id: str,
    ) -> dict:
        return {
            "configurable": {
                "thread_id": thread_id
            },
            "recursion_limit": 30,
        }

    async def chat(
        self,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
        question: str,
        is_new_conversation: bool = False,
    ) -> dict:
        thread_id = self.build_thread_id(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        config = self.build_config(thread_id)
        context = self.build_context(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        input_state = (
            create_initial_state(question)
            if is_new_conversation
            else append_user_message(question)
        )

        result = await self.graph.ainvoke(
            input_state,
            config=config,
            context=context,
        )

        return {
            "thread_id": thread_id,
            "answer": result.get("final_answer", ""),
            "intent": result.get("intent"),
            "order_id": result.get("order_id"),
            "order_info": result.get("order_info"),
            "risk_level": result.get("risk_level"),
            "need_human_confirm": result.get("need_human_confirm"),
            "pending_action": result.get("pending_action"),
            "pending_payload": result.get("pending_payload"),
            "recalled_memories": result.get("recalled_memories", []),
            "sources": result.get("sources", []),
            "logs": result.get("logs", []),
            "errors": result.get("errors", []),
        }

    async def resume(
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
        context = self.build_context(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        result = await self.graph.ainvoke(
            Command(resume=decision),
            config=config,
            context=context,
        )

        return {
            "thread_id": thread_id,
            "answer": result.get("final_answer", ""),
            "human_decision": result.get("human_decision"),
            "action_result": result.get("action_result"),
            "logs": result.get("logs", []),
            "errors": result.get("errors", []),
        }

    async def get_state(
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

        snapshot = await self.graph.aget_state(config)

        return {
            "thread_id": thread_id,
            "values": snapshot.values,
            "next": snapshot.next,
            "config": snapshot.config,
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

        return [
            {
                "key": item.key,
                "value": item.value,
            }
            for item in self.store.search(namespace)
        ]


langgraph_ecommerce_agent_service = LangGraphEcommerceAgentService()