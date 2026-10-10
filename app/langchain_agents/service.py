from app.core.exceptions import AppException, ErrorCode
from app.core.logging import get_logger
from app.langchain_agents.factory import (
    build_ecommerce_agent,
    parse_agent_result,
)
from app.langchain_agents.schemas import AgentRunResponse


logger = get_logger(__name__)


class LangChainAgentService:
    async def run_ecommerce_agent(
        self,
        user_question: str,
        provider: str = "deepseek",
        model_name: str = "deepseek-chat",
    ) -> AgentRunResponse:
        logger.info(
            f"langchain_agent_start provider={provider} model={model_name}"
        )

        try:
            agent = build_ecommerce_agent(
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

            parsed = parse_agent_result(result)

        except Exception as exc:
            logger.exception("langchain_agent_run_failed")

            raise AppException(
                message="LangChain Agent 执行失败",
                code=ErrorCode.LLM_CALL_FAILED,
                status_code=500,
                data={
                    "provider": provider,
                    "model": model_name,
                    "error": repr(exc),
                },
            ) from exc

        logger.info(
            f"langchain_agent_success used_tools={parsed.used_tools} "
            f"tool_call_count={len(parsed.tool_calls)}"
        )

        return parsed


langchain_agent_service = LangChainAgentService()