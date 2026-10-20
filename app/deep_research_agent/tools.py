from app.deep_research_agent.schemas import ResearchSource
from app.deep_research_agent.sources import ResearchSourceFactory


class MockWebSearchTool:
    """
    教学版外部搜索工具。

    生产环境可替换为：
    1. Tavily 
    2. Bing Search
    3. SerpAPI
    4. 自建搜索服务
    """

    def __init__(self):
        self.source_factory = ResearchSourceFactory()

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[ResearchSource]:
        candidates = [
            (
                "AI Agent 平台趋势",
                "AI Agent 平台正在从单点 Chatbot 走向可编排、可观测、可评估的企业级 Agent 平台。",
            ),
            (
                "Deep Research 场景",
                "Deep Research 类任务通常需要规划、资料检索、分析、写作、审查和来源追踪。",
            ),
            (
                "多 Agent 协作",
                "复杂任务可以通过 Research、Analysis、Writer、Reviewer 等 Sub-Agent 分工完成。",
            ),
            (
                "企业落地风险",
                "企业落地 AI Agent 需要关注权限、数据安全、成本、可观测性、评估和人工确认。",
            ),
            (
                "RAG 与 Agent 结合",
                "RAG 可以为 Agent 提供企业内部知识来源，Agent 则负责围绕目标进行规划和执行。",
            ),
        ]

        return [
            self.source_factory.create_web_source(
                title=title,
                content=f"查询：{query}\n{content}",
                url=f"https://example.com/{index}",
                score=0.9 - index * 0.05,
            )
            for index, (title, content) in enumerate(candidates[:limit])
        ]


class MockEnterpriseKBTool:
    """
    教学版企业知识库工具。

    生产环境可替换为第 45 章企业 AI 知识库项目的检索接口。
    """

    def __init__(self):
        self.source_factory = ResearchSourceFactory()

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[ResearchSource]:
        candidates = [
            (
                "企业知识库 RAG 架构",
                "企业知识库包含文档解析、Chunk、Embedding、Vector Store、高级 Retrieval 和 Evaluation。",
            ),
            (
                "DeepAgents 内部规范",
                "复杂任务应先 Planning，再通过 Sub-Agent 分工，长内容写入 Workspace。",
            ),
            (
                "Agent 安全规范",
                "高风险工具调用需要权限校验、Human-in-the-loop、日志审计和 Trace 记录。",
            ),
            (
                "Context 管理规范",
                "messages 只放当前必要信息，长工具结果和 Sub-Agent 原始输出应写入 workspace。",
            ),
        ]

        return [
            self.source_factory.create_kb_source(
                title=title,
                content=f"查询：{query}\n{content}",
                file_path=f"/kb/{index}.md",
                score=0.95 - index * 0.04,
            )
            for index, (title, content) in enumerate(candidates[:limit])
        ]