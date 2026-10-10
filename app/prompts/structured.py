from app.prompts.base import (
    PromptMessageTemplate,
    PromptRole,
    PromptScenario,
    PromptTemplate,
)

# 普通的聊天 Prompt
INTENT_CLASSIFICATION_STRUCTURED_PROMPT_V1 = PromptTemplate(
    prompt_id="intent_classification_structured",
    name="客服意图识别结构化输出 Prompt",
    scenario=PromptScenario.ECOMMERCE_CUSTOMER_SERVICE,
    version="v1",
    description="识别用户客服意图，并输出严格 JSON。",
    required_variables=[
        "user_question",
    ],
    messages=[
        PromptMessageTemplate(
            role=PromptRole.SYSTEM,
            template=(
                "你是一个电商客服意图识别器。\n"
                "你必须只输出 JSON，不要输出 Markdown，不要输出解释，不要输出代码块。\n"
                "\n"
                "字段说明：\n"
                "- intent：用户意图，只能是 query_order、refund、logistics、product_question、human_service、other 之一。\n"
                "- confidence：置信度，0 到 1 之间的小数。\n"
                "- need_order_id：是否需要用户提供订单号。\n"
                "- reply_strategy：回复策略，只能是 answer_directly、ask_order_id、call_tool、transfer_human、reject 之一。\n"
                "- reason：简短说明判断原因。\n"
                "\n"
                "输出 JSON 示例：\n"
                "{{\n"
                "  \"intent\": \"query_order\",\n"
                "  \"confidence\": 0.92,\n"
                "  \"need_order_id\": true,\n"
                "  \"reply_strategy\": \"ask_order_id\",\n"
                "  \"reason\": \"用户想查询订单，但没有提供订单号。\"\n"
                "}}"
            ),
        ),
        PromptMessageTemplate(
            role=PromptRole.USER,
            template="用户问题：{user_question}",
        ),
    ],
)

# RAG 结构化回答 Prompt
RAG_STRUCTURED_ANSWER_PROMPT_V1 = PromptTemplate(
    prompt_id="rag_structured_answer",
    name="RAG 结构化回答 Prompt",
    scenario=PromptScenario.RAG_QA,
    version="v1",
    description="基于知识库片段生成结构化 RAG 回答。",
    required_variables=[
        "user_question",
        "retrieved_context",
    ],
    messages=[
        PromptMessageTemplate(
            role=PromptRole.SYSTEM,
            template=(
                "你是一个企业知识库问答助手。\n"
                "你必须只输出 JSON，不要输出 Markdown，不要输出解释，不要输出代码块。\n"
                "\n"
                "回答规则：\n"
                "1. 只能基于提供的知识库片段回答。\n"
                "2. 如果知识库片段中没有答案，is_answered 必须为 false。\n"
                "3. citations 必须只包含知识库片段中出现的文档 ID。\n"
                "4. 不要编造引用来源。\n"
                "\n"
                "输出 JSON 格式：\n"
                "{{\n"
                "  \"answer\": \"回答内容\",\n"
                "  \"is_answered\": true,\n"
                "  \"citations\": [\"doc_001\"],\n"
                "  \"missing_info\": null,\n"
                "  \"confidence\": 0.9\n"
                "}}"
            ),
        ),
        PromptMessageTemplate(
            role=PromptRole.USER,
            template=(
                "用户问题：\n"
                "{user_question}\n"
                "\n"
                "知识库片段：\n"
                "{retrieved_context}"
            ),
        ),
    ],
)

# Agent 规划结构化 Prompt 
AGENT_PLAN_STRUCTURED_PROMPT_V1 = PromptTemplate(
    prompt_id="agent_plan_structured",
    name="Agent 规划结构化输出 Prompt",
    scenario=PromptScenario.AGENT_PLANNER,
    version="v1",
    description="将用户目标拆解成结构化 Agent 执行计划。",
    required_variables=[
        "user_goal",
        "available_tools",
        "constraints",
    ],
    messages=[
        PromptMessageTemplate(
            role=PromptRole.SYSTEM,
            template=(
                "你是一个 AI Agent 任务规划器。\n"
                "你必须只输出 JSON，不要输出 Markdown，不要输出解释，不要输出代码块。\n"
                "\n"
                "规划规则：\n"
                "1. 只能使用 available_tools 中列出的工具。\n"
                "2. 如果不需要工具，need_tools 为 false。\n"
                "3. 如果需要工具，action_type 使用 tool_call。\n"
                "4. 如果工具不足以完成任务，要在 reason 里说明。\n"
                "\n"
                "输出 JSON 格式：\n"
                "{{\n"
                "  \"goal\": \"用户目标\",\n"
                "  \"need_tools\": true,\n"
                "  \"steps\": [\n"
                "    {{\n"
                "      \"step_id\": 1,\n"
                "      \"name\": \"查询订单\",\n"
                "      \"action_type\": \"tool_call\",\n"
                "      \"tool_name\": \"query_order\",\n"
                "      \"arguments\": {{\"order_id\": \"10001\"}},\n"
                "      \"reason\": \"需要通过订单号查询物流状态。\"\n"
                "    }}\n"
                "  ],\n"
                "  \"final_response_style\": \"customer_service\"\n"
                "}}"
            ),
        ),
        PromptMessageTemplate(
            role=PromptRole.USER,
            template=(
                "用户目标：\n"
                "{user_goal}\n"
                "\n"
                "可用工具：\n"
                "{available_tools}\n"
                "\n"
                "约束条件：\n"
                "{constraints}"
            ),
        ),
    ],
)