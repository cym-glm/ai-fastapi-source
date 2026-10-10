from app.prompts.base import (
    PromptMessageTemplate,
    PromptRole,
    PromptScenario,
    PromptTemplate,
)


GENERAL_CHAT_PROMPT_V1 = PromptTemplate(
    prompt_id="general_chat",
    name="通用聊天助手",
    scenario=PromptScenario.GENERAL_CHAT,
    version="v1",
    description="用于普通 AI Chat 的基础 Prompt。",
    required_variables=[
        "user_question",
    ],
    messages=[
        PromptMessageTemplate(
            role=PromptRole.SYSTEM,
            template=(
                "你是一个专业、耐心、表达清晰的 AI 助手。\n"
                "回答要求：\n"
                "1. 优先用中文回答。\n"
                "2. 不要编造事实。\n"
                "3. 如果不确定，请明确说明不确定。\n"
                "4. 回答要结构清晰，不要啰嗦。"
            ),
        ),
        PromptMessageTemplate(
            role=PromptRole.USER,
            template="{user_question}",
        ),
    ],
)