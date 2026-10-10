from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import BaseMessage

from app.langchain_agents.schemas import AgentMessageItem, AgentRunResponse
from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_tools.registry import langchain_tool_registry


def build_agent_model(
    provider: str = "deepseek",
    model_name: str = "deepseek-chat",
    temperature: float = 0,
):
    return LangChainModelFactory.create(
        provider=provider,
        model=model_name,
        temperature=temperature,
    )


def build_ecommerce_agent(
    provider: str = "deepseek",
    model_name: str = "deepseek-chat",
):
    model = build_agent_model(
        provider=provider,
        model_name=model_name,
        temperature=0,
    )

    tools = langchain_tool_registry.get_many([
        "query_order",
        "query_logistics",
        "transfer_human",
    ])

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "你是一个跨境电商平台的智能客服 Agent。\n"
            "\n"
            "你可以使用工具查询订单、物流和创建转人工工单。\n"
            "\n"
            "核心规则：\n"
            "1. 用户询问订单状态、发货状态、物流状态时，优先调用工具查询真实信息。\n"
            "2. 不要编造订单状态、物流公司或物流单号。\n"
            "3. 如果用户没有提供订单号，要先追问订单号，不要调用 query_order。\n"
            "4. 如果工具返回未查询到订单，要礼貌说明，并建议用户检查订单号。\n"
            "5. 如果问题超出客服范围，建议转人工。\n"
            "6. 回复要简洁、礼貌、可执行。"
        ),
    )


def message_to_item(message: BaseMessage) -> AgentMessageItem:
    tool_calls = getattr(message, "tool_calls", None) or []
    tool_call_id = getattr(message, "tool_call_id", None)
    name = getattr(message, "name", None)

    content = message.content

    if isinstance(content, list):
        content_text = str(content)
    else:
        content_text = str(content or "")

    return AgentMessageItem(
        type=message.type,
        content=content_text,
        name=name,
        tool_calls=tool_calls,
        tool_call_id=tool_call_id,
    )


def parse_agent_result(result: dict[str, Any]) -> AgentRunResponse:
    messages = result.get("messages", [])

    items = [
        message_to_item(message)
        for message in messages
    ]

    answer = ""

    if messages:
        answer = str(messages[-1].content or "")

    all_tool_calls: list[dict[str, Any]] = []

    for message in messages:
        tool_calls = getattr(message, "tool_calls", None) or []
        all_tool_calls.extend(tool_calls)

    return AgentRunResponse(
        answer=answer,
        messages=items,
        used_tools=bool(all_tool_calls),
        tool_calls=all_tool_calls,
        metadata={
            "message_count": len(messages),
            "tool_call_count": len(all_tool_calls),
        },
    )