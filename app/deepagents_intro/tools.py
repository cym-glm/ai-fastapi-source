from app.deepagents_intro.schemas import ToolResult


class MockResearchTool:
    def search(
        self,
        query: str,
    ) -> ToolResult:
        if "AI Agent 平台" in query or "竞品" in query:
            output = (
                "模拟搜索结果：\n"
                "1. Dify：偏应用编排和企业知识库。\n"
                "2. Coze：偏低门槛 Bot 和工作流搭建。\n"
                "3. LangGraph：偏开发者 Agent 编排框架。\n"
                "4. AutoGen：偏多 Agent 协作研究。\n"
                "5. CrewAI：偏角色化 Agent 团队协作。"
            )
        elif "RAG" in query:
            output = (
                "模拟搜索结果：RAG 企业知识库通常包含文档解析、"
                "Chunk、Embedding、Vector Store、Retrieval、Evaluation。"
            )
        else:
            output = (
                f"模拟搜索结果：找到与「{query}」相关的资料，"
                "但需要进一步整理。"
            )

        return ToolResult(
            tool_name="mock_search",
            input=query,
            output=output,
        )


class MockAnalysisTool:
    def analyze(
        self,
        content: str,
    ) -> ToolResult:
        output = (
            "分析结论：\n"
            "1. 低门槛平台更适合业务人员快速搭建。\n"
            "2. 开发者框架更适合复杂企业系统集成。\n"
            "3. 企业级 Agent 平台通常需要 RAG、工具调用、权限、日志、评估和部署能力。\n"
            "4. 趋势是从单点 Chatbot 走向可编排、可观测、可评估的 Agent 平台。"
        )

        return ToolResult(
            tool_name="mock_analyze",
            input=content,
            output=output,
        )