from app.core.exceptions import AppException, ErrorCode
from app.core.logging import get_logger
from app.langchain_agent_rag.factory import (
    build_ecommerce_agent_with_rag,
    parse_agent_rag_result,
)
from app.langchain_agent_rag.index import ensure_rag_index
from app.langchain_agent_rag.schemas import AgentRAGRunResponse


logger = get_logger(__name__)


class LangChainAgentRAGService:
    async def run_ecommerce_agent_rag(
        self,
        user_question: str,
        provider: str = "deepseek",
        model_name: str = "deepseek-chat",
    ) -> AgentRAGRunResponse:
        logger.info(
            f"langchain_agent_rag_start provider={provider} model={model_name}"
        )

        try:
            index_result = ensure_rag_index()

            agent = build_ecommerce_agent_with_rag(
                provider=provider,
                model_name=model_name,
            )

            result = await agent.ainvoke({
                "messages": [
                    {
                        "role": "user",
                        "content": user_question,
                    }
                ]
            })

            parsed = parse_agent_rag_result(result)
            parsed.metadata["index"] = index_result

        except Exception as exc:
            logger.exception("langchain_agent_rag_failed")

            raise AppException(
                message="LangChain Agent + RAG 执行失败",
                code=ErrorCode.LLM_CALL_FAILED,
                status_code=500,
                data={
                    "provider": provider,
                    "model": model_name,
                    "error": repr(exc),
                },
            ) from exc

        logger.info(
            f"langchain_agent_rag_success used_tools={parsed.used_tools} "
            f"used_rag={parsed.used_rag} "
            f"tool_count={len(parsed.tool_calls)} "
            f"source_count={len(parsed.sources)}"
        )

        return parsed


langchain_agent_rag_service = LangChainAgentRAGService()