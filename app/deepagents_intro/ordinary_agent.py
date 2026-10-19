from app.deepagents_intro.tools import MockResearchTool


class OrdinaryAgent:
    """
    普通 Agent 教学版。

    特点：
    1. 不做任务拆解。
    2. 不维护 todo。
    3. 不写 workspace。
    4. 不委派 subagent。
    5. 只根据当前问题直接回答。
    """

    def __init__(self):
        self.search_tool = MockResearchTool()

    def run(
        self,
        user_request: str,
    ) -> str:
        if "调研" in user_request or "竞品" in user_request:
            search_result = self.search_tool.search(user_request)
            return (
                "我查到了一些资料：\n"
                f"{search_result.output}\n\n"
                "简单结论：AI Agent 平台正在从简单聊天机器人，"
                "升级到具备工作流、知识库、工具调用和多 Agent 协作能力的平台。"
            )

        return "这是一个普通 Agent 的简单回答。"