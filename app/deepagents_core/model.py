from app.deepagents_core.schemas import (
    DeepAgentMessage,
    DeepTodo,
    DeepTodoStatus,
)


class TeachingChatModel:
    """
    教学版模型。

    说明：
    真实项目里这里会替换成 ChatOpenAI / ChatAnthropic / ChatGoogleGenerativeAI。
    """

    def __init__(
        self,
        model_name: str = "teaching-model",
    ):
        self.model_name = model_name

    def make_plan(
        self,
        user_request: str,
    ) -> list[DeepTodo]:
        if "调研" in user_request or "报告" in user_request:
            return [
                DeepTodo("todo_001", "明确任务目标"),
                DeepTodo("todo_002", "收集资料"),
                DeepTodo("todo_003", "分析资料"),
                DeepTodo("todo_004", "生成报告草稿"),
                DeepTodo("todo_005", "检查和完善报告"),
                DeepTodo("todo_006", "输出最终结果"),
            ]

        return [
            DeepTodo("todo_001", "理解用户问题"),
            DeepTodo("todo_002", "调用必要工具"),
            DeepTodo("todo_003", "输出回答"),
        ]

    def summarize_messages(
        self,
        messages: list[DeepAgentMessage],
    ) -> str:
        if not messages:
            return ""

        return "\n".join(
            f"{message.role}: {message.content}"
            for message in messages
        )

    def generate_final_answer(
        self,
        user_request: str,
        research_notes: str,
        analysis_notes: str,
    ) -> str:
        return f"""
            # DeepAgent 执行结果
            ## 一、用户任务
            {user_request}
            ## 二、资料整理
            {research_notes}
            ## 三、分析结论
            {analysis_notes}
            ## 四、最终结论

            这个任务适合使用 DeepAgents，因为它不是一次工具调用能完成的短任务，而是需要规划、资料收集、分析、写作、检查和最终交付的复杂任务。
""".strip()