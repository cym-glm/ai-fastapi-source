from langchain_core.messages import BaseMessage

from app.langchain_prompts.service import langchain_prompt_service
from app.prompts.base import PromptScenario
from app.schemas.chat import ChatRequest, MessageRole


def build_history_from_chat_request(
    request: ChatRequest,
) -> list[BaseMessage]:
    history = []

    for message in request.messages[:-1]:
        if message.role == MessageRole.USER:
            history.append(("human", message.content))

        elif message.role == MessageRole.ASSISTANT:
            history.append(("ai", message.content))

    return history


def build_langchain_messages_from_chat_request(
    request: ChatRequest,
) -> list[BaseMessage]:
    latest_user_question = ""

    for message in reversed(request.messages):
        if message.role == MessageRole.USER:
            latest_user_question = message.content
            break

    scenario = PromptScenario(request.prompt_scenario or PromptScenario.GENERAL_CHAT.value)

    variables = {
        "history": build_history_from_chat_request(request),
        "user_question": latest_user_question,
    }

    if scenario == PromptScenario.ECOMMERCE_CUSTOMER_SERVICE:
        variables["business_rules"] = request.metadata.get(
            "business_rules",
            "暂无额外业务规则。",
        )
        variables["order_info"] = request.metadata.get(
            "order_info",
            "用户未提供订单信息。",
        )

    if scenario == PromptScenario.RAG_QA:
        variables["retrieved_context"] = request.metadata.get(
            "retrieved_context",
            "暂无检索上下文。",
        )

    if scenario == PromptScenario.AGENT_PLANNER:
        variables["user_goal"] = latest_user_question
        variables["available_tools"] = request.metadata.get(
            "available_tools",
            "暂无可用工具。",
        )
        variables["constraints"] = request.metadata.get(
            "constraints",
            "无。",
        )

    return langchain_prompt_service.render_messages_by_scenario(
        scenario=scenario,
        version=request.prompt_version or "v1",
        variables=variables,
    )