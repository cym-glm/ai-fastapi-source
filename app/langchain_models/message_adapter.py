from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from app.llm.schemas import (
    LLMMessage,
    LLMResponse,
    LLMRole,
    LLMToolCall,
    LLMUsage,
)
from app.llm.schemas import LLMProviderName


def to_langchain_message(message: LLMMessage) -> BaseMessage:
    if message.role == LLMRole.SYSTEM:
        return SystemMessage(content=message.content)

    if message.role == LLMRole.USER:
        return HumanMessage(content=message.content)

    if message.role == LLMRole.ASSISTANT:
        return AIMessage(content=message.content)

    if message.role == LLMRole.TOOL:
        if not message.tool_call_id:
            raise ValueError("ToolMessage 必须提供 tool_call_id")

        return ToolMessage(
            content=message.content,
            tool_call_id=message.tool_call_id,
        )

    raise ValueError(f"不支持的消息角色：{message.role}")


def to_langchain_messages(messages: list[LLMMessage]) -> list[BaseMessage]:
    return [
        to_langchain_message(message)
        for message in messages
    ]


def to_llm_usage(ai_message: AIMessage) -> LLMUsage:
    usage = ai_message.usage_metadata or {}

    return LLMUsage(
        prompt_tokens=usage.get("input_tokens", 0),
        completion_tokens=usage.get("output_tokens", 0),
        total_tokens=usage.get("total_tokens", 0),
    )


def to_llm_tool_calls(ai_message: AIMessage) -> list[LLMToolCall]:
    tool_calls: list[LLMToolCall] = []

    for item in ai_message.tool_calls or []:
        tool_calls.append(
            LLMToolCall(
                id=item.get("id", ""),
                name=item.get("name", ""),
                arguments=item.get("args", {}),
                raw_arguments="",
            )
        )

    return tool_calls


def to_llm_response(
    ai_message: AIMessage,
    provider: LLMProviderName,
    model: str,
) -> LLMResponse:
    return LLMResponse(
        provider=provider,
        model=model,
        content=str(ai_message.content or ""),
        usage=to_llm_usage(ai_message),
        tool_calls=to_llm_tool_calls(ai_message),
        finish_reason=(ai_message.response_metadata or {}).get("finish_reason"),
        raw_response={
            "id": ai_message.id,
            "response_metadata": ai_message.response_metadata,
            "usage_metadata": ai_message.usage_metadata,
            "tool_calls": ai_message.tool_calls,
        },
    )