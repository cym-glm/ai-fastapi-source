from app.prompts.base import (
    PromptMessageTemplate,
    PromptRole,
    PromptScenario,
    PromptTemplate,
)


AGENT_PLANNER_PROMPT_V1 = PromptTemplate(
    prompt_id="agent_planner",
    name="Agent 任务规划 Prompt",
    scenario=PromptScenario.AGENT_PLANNER,
    version="v1",
    description="用于 Agent 执行前的任务分析与步骤规划。",
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
                "\n"
                "你的任务：\n"
                "1. 分析用户目标。\n"
                "2. 判断是否需要调用工具。\n"
                "3. 拆解执行步骤。\n"
                "4. 每一步都要说明目的。\n"
                "5. 不要调用不存在的工具。\n"
                "6. 如果工具不足以完成任务，要明确说明。\n"
                "7. 输出要结构化，便于程序读取。"
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
                "{constraints}\n"
                "\n"
                "请输出任务规划。"
            ),
        ),
    ],
)