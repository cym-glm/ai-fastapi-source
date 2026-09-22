from typing import Any

from langchain_core.messages import ToolMessage

from app.core.logging import get_logger
from app.langchain_tools.registry import langchain_tool_registry


logger = get_logger(__name__)


class LangChainToolExecutionError(Exception):
    def __init__(
        self,
        message: str,
        tool_name: str,
        detail: str | None = None,
    ):
        self.message = message
        self.tool_name = tool_name
        self.detail = detail
        super().__init__(message)


class LangChainToolExecutor:
    async def execute_tool_call(
        self,
        tool_call: dict[str, Any],
    ) -> ToolMessage:
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args") or {}
        tool_call_id = tool_call.get("id")

        if not tool_name:
            raise LangChainToolExecutionError(
                message="tool_call 缺少工具名称",
                tool_name="unknown",
                detail=str(tool_call),
            )

        if not tool_call_id:
            raise LangChainToolExecutionError(
                message="tool_call 缺少 id",
                tool_name=tool_name,
                detail=str(tool_call),
            )

        try:
            tool = langchain_tool_registry.get(tool_name)

        except KeyError as exc:
            raise LangChainToolExecutionError(
                message="工具不存在",
                tool_name=tool_name,
                detail=str(exc),
            ) from exc

        logger.info(
            f"langchain_tool_execute_start tool_name={tool_name} "
            f"tool_call_id={tool_call_id}"
        )

        try:
            result = await tool.ainvoke(tool_args)

        except Exception as exc:
            logger.exception(
                f"langchain_tool_execute_failed tool_name={tool_name}"
            )

            result = {
                "success": False,
                "error": "工具执行失败",
                "detail": repr(exc),
            }

        else:
            result = {
                "success": True,
                "data": result,
            }

        logger.info(
            f"langchain_tool_execute_success tool_name={tool_name} "
            f"tool_call_id={tool_call_id}"
        )

        return ToolMessage(
            content=str(result),
            tool_call_id=tool_call_id,
            name=tool_name,
        )

    async def execute_tool_calls(
        self,
        tool_calls: list[dict[str, Any]],
    ) -> list[ToolMessage]:
        messages = []

        for tool_call in tool_calls:
            message = await self.execute_tool_call(tool_call)
            messages.append(message)

        return messages


langchain_tool_executor = LangChainToolExecutor()