from app.prompts.base import (
    PromptMessageTemplate,
    PromptRole,
    PromptScenario,
    PromptTemplate,
)


RAG_QA_PROMPT_V1 = PromptTemplate(
    prompt_id="rag_qa",
    name="企业知识库问答 Prompt",
    scenario=PromptScenario.RAG_QA,
    version="v1",
    description="用于 RAG 知识库问答，要求基于检索文档回答。",
    required_variables=[
        "user_question",
        "retrieved_context",
    ],
    messages=[
        PromptMessageTemplate(
            role=PromptRole.SYSTEM,
            template=(
                "你是一个企业知识库问答助手。\n"
                "\n"
                "回答规则：\n"
                "1. 你只能基于提供的知识库片段回答。\n"
                "2. 如果知识库片段中没有答案，请回答：知识库中暂未找到相关信息。\n"
                "3. 不要编造不存在的政策、数据、流程、链接。\n"
                "4. 回答要简洁、准确。\n"
                "5. 如果文档片段之间存在冲突，请说明存在冲突，不要强行合并。\n"
                "6. 如果能找到依据，请在回答末尾列出引用来源编号。"
            ),
        ),
        PromptMessageTemplate(
            role=PromptRole.USER,
            template=(
                "用户问题：\n"
                "{user_question}\n"
                "\n"
                "知识库片段：\n"
                "{retrieved_context}\n"
                "\n"
                "请基于知识库片段回答用户问题。"
            ),
        ),
    ],
)