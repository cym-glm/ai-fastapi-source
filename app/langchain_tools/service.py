from langchain_core.messages import HumanMessage, SystemMessage

from app.core.exceptions import AppException, ErrorCode
from app.core.logging import get_logger
from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_tools.executor import (
    LangChainToolExecutionError,
    langchain_tool_executor,
)
from app.langchain_tools.registry import langchain_tool_registry


logger = get_logger(__name__)


class LangChainToolCallingService:
    async def run_ecommerce_customer_service(
        self,
        user_question: str,
        provider: str = "deepseek",
        model_name: str = "deepseek-chat",
    ) -> dict:
        model = LangChainModelFactory.create(
            provider=provider,
            model=model_name,
            temperature=0,
        )

        tools = langchain_tool_registry.get_many([
            "query_order",
            "query_logistics",
            "transfer_human",
        ])

        model_with_tools = model.bind_tools(tools)

        messages = [
            SystemMessage(
                content=(
                    "你是一个跨境电商客服助手。\n"
                    "当用户询问订单、物流、发货状态时，优先调用工具查询真实信息。\n"
                    "不要编造订单状态、物流公司或物流单号。\n"
                    "如果用户没有提供订单号，应先追问订单号，不要调用 query_order。\n"
                    "工具返回结果后，请用礼貌、简洁的中文回复用户。"
                )
            ),
            HumanMessage(content=user_question),
        ]

        logger.info(
            f"langchain_tool_calling_start model={model_name}"
        )

        try:
            first_response = await model_with_tools.ainvoke(messages)

        except Exception as exc:
            logger.exception("langchain_tool_model_first_call_failed")

            raise AppException(
                message="LangChain 工具调用前模型请求失败",
                code=ErrorCode.LLM_CALL_FAILED,
                status_code=500,
                data={
                    "error": repr(exc),
                    "provider": provider,
                    "model": model_name,
                },
            ) from exc

        if not first_response.tool_calls:
            return {
                "answer": first_response.content,
                "tool_calls": [],
                "tool_messages": [],
                "metadata": {
                    "used_tools": False,
                },
            }

        try:
            tool_messages = await langchain_tool_executor.execute_tool_calls(
                first_response.tool_calls
            )

        except LangChainToolExecutionError as exc:
            logger.exception(
                f"langchain_tool_execute_error tool={exc.tool_name}"
            )

            raise AppException(
                message=exc.message,
                code=ErrorCode.INTERNAL_ERROR,
                status_code=500,
                data={
                    "tool_name": exc.tool_name,
                    "detail": exc.detail,
                },
            ) from exc

        messages.append(first_response)
        messages.extend(tool_messages)

        try:
            final_response = await model.ainvoke(messages)

        except Exception as exc:
            logger.exception("langchain_tool_model_final_call_failed")

            raise AppException(
                message="LangChain 工具调用后模型总结失败",
                code=ErrorCode.LLM_CALL_FAILED,
                status_code=500,
                data={
                    "error": repr(exc),
                    "provider": provider,
                    "model": model_name,
                },
            ) from exc

        logger.info(
            f"langchain_tool_calling_success model={model_name} "
            f"tool_count={len(first_response.tool_calls)}"
        )

        return {
            "answer": final_response.content,
            "tool_calls": first_response.tool_calls,
            "tool_messages": [
                {
                    "tool_call_id": message.tool_call_id,
                    "name": message.name,
                    "content": message.content,
                }
                for message in tool_messages
            ],
            "metadata": {
                "used_tools": True,
                "provider": provider,
                "model": model_name,
            },
        }


langchain_tool_calling_service = LangChainToolCallingService()