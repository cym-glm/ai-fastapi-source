import json
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import BaseMessage

from app.langchain_agent_rag.schemas import (
    AgentRAGMessageItem,
    AgentRAGRunResponse,
    AgentRAGSource,
)
from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_rag.tools import search_knowledge_base_tool
from app.langchain_tools.registry import langchain_tool_registry


def build_agent_rag_model(
    provider: str = "deepseek",
    model_name: str = "deepseek-chat",
    temperature: float = 0,
):
    return LangChainModelFactory.create(
        provider=provider,
        model=model_name,
        temperature=temperature,
    )


def build_ecommerce_agent_with_rag(
    provider: str = "deepseek",
    model_name: str = "deepseek-chat",
):
    model = build_agent_rag_model(
        provider=provider,
        model_name=model_name,
        temperature=0,
    )

    business_tools = langchain_tool_registry.get_many([
        "query_order",
        "query_logistics",
        "transfer_human",
    ])

    tools = [
        *business_tools,
        search_knowledge_base_tool,
    ]

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "你是一个跨境电商平台的智能客服 Agent。\n"
            "\n"
            "你可以使用两类工具：\n"
            "1. 业务工具：查询订单、查询物流、创建人工客服工单。\n"
            "2. 知识库工具：查询售后规则、退款规则、课程说明、员工制度等文档内容。\n"
            "\n"
            "核心规则：\n"
            "1. 当用户询问订单状态、发货状态、物流状态时，优先调用 query_order 或 query_logistics。\n"
            "2. 当用户询问退款规则、售后规则、公司制度、课程阶段等知识性问题时，优先调用 search_knowledge_base。\n"
            "3. 当用户问题同时包含订单状态和规则判断时，可以先调用 query_order，再调用 search_knowledge_base。\n"
            "4. 不要编造订单状态、物流公司、物流单号。\n"
            "5. 不要编造售后规则、退款规则、公司制度。\n"
            "6. 如果知识库工具返回无法确认，要明确说明无法从知识库确认。\n"
            "7. 如果用户没有提供订单号，不要调用 query_order，要先追问订单号。\n"
            "8. 如果问题超出 AI 能力范围，建议转人工。\n"
            "9. 最终回答要简洁、礼貌、可执行。\n"
            "10. 如果回答使用了知识库内容，要在回答中说明依据来自知识库。"
        ),
    )


def message_to_item(message: BaseMessage) -> AgentRAGMessageItem:
    tool_calls = getattr(message, "tool_calls", None) or []
    tool_call_id = getattr(message, "tool_call_id", None)
    name = getattr(message, "name", None)

    content = message.content

    if isinstance(content, list):
        content_text = str(content)
    else:
        content_text = str(content or "")

    return AgentRAGMessageItem(
        type=message.type,
        content=content_text,
        name=name,
        tool_calls=tool_calls,
        tool_call_id=tool_call_id,
    )


def extract_sources_from_tool_message_content(
    content: str,
) -> list[AgentRAGSource]:
    """
    从 search_knowledge_base 工具返回的 JSON 字符串中提取 sources。

    注意：
    本章 RAG Tool 返回的是 RAGAnswer.model_dump() 的 JSON。
    如果后面调整工具返回结构，这里也要同步调整。
    """
    try:
        data = json.loads(content)

    except Exception:
        return []

    raw_sources = data.get("sources") or []

    sources = []

    for item in raw_sources:
        if not isinstance(item, dict):
            continue

        sources.append(
            AgentRAGSource(
                document_id=item.get("document_id"),
                chunk_id=item.get("chunk_id"),
                source=item.get("source"),
                content_preview=item.get("content_preview", ""),
            )
        )

    return sources


def parse_agent_rag_result(
    result: dict[str, Any],
) -> AgentRAGRunResponse:
    messages = result.get("messages", [])

    items = [
        message_to_item(message)
        for message in messages
    ]

    answer = ""

    if messages:
        answer = str(messages[-1].content or "")

    all_tool_calls: list[dict[str, Any]] = []
    sources: list[AgentRAGSource] = []
    used_rag = False

    for message in messages:
        tool_calls = getattr(message, "tool_calls", None) or []
        all_tool_calls.extend(tool_calls)

        if message.type == "tool":
            name = getattr(message, "name", None)

            if name == "search_knowledge_base":
                used_rag = True
                sources.extend(
                    extract_sources_from_tool_message_content(
                        str(message.content or "")
                    )
                )

    return AgentRAGRunResponse(
        answer=answer,
        used_tools=bool(all_tool_calls),
        used_rag=used_rag,
        tool_calls=all_tool_calls,
        messages=items,
        sources=sources,
        metadata={
            "message_count": len(messages),
            "tool_call_count": len(all_tool_calls),
            "source_count": len(sources),
        },
    )