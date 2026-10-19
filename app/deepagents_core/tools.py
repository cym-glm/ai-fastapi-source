from app.deepagents_core.schemas import (
    DeepTool,
    DeepToolResult,
)


def search_enterprise_knowledge_base(query: str) -> str:
    """
    Search enterprise knowledge base.

    Use this tool when the user asks about internal documents,
    RAG, AI Agent platform, refund policy, or enterprise knowledge.
    """
    if "DeepAgents" in query or "复杂任务" in query:
        return (
            "企业知识库资料：DeepAgents 适合复杂长任务，"
            "通常包含 Planning、Todo、Workspace、SubAgents、Context 管理等能力。"
        )

    if "RAG" in query or "知识库" in query:
        return (
            "企业知识库资料：RAG 链路包括文档解析、Chunk、Embedding、Vector Store、"
            "高级 Retrieval、Grounded Answer 和 Evaluation。"
        )

    return f"企业知识库中找到与「{query}」相关的资料。"


def web_research(query: str) -> str:
    """
    Research public information.

    Use this tool when the task needs external background research.
    """
    return (
        f"模拟外部调研结果：{query} 相关方向包括 Agent 平台、"
        "工作流编排、多 Agent 协作、RAG、工具调用和可观测性。"
    )


def create_report(title: str, content: str) -> str:
    """
    Create a markdown report.

    Use this tool when the agent needs to generate a report artifact.
    """
    return f"# {title}\n\n{content}"


def send_email(to: str, subject: str, content: str) -> str:
    """
    Send an email.

    This is a high-risk write operation and should require confirmation.
    """
    return f"已模拟发送邮件给 {to}，主题：{subject}"


def build_default_tools() -> list[DeepTool]:
    return [
        DeepTool(
            name="search_enterprise_knowledge_base",
            description="检索企业内部知识库。",
            func=search_enterprise_knowledge_base,
        ),
        DeepTool(
            name="web_research",
            description="进行外部资料调研。",
            func=web_research,
        ),
        DeepTool(
            name="create_report",
            description="生成 Markdown 报告。",
            func=create_report,
        ),
        DeepTool(
            name="send_email",
            description="发送邮件，高风险写操作，需要人工确认。",
            func=send_email,
            requires_confirmation=True,
        ),
    ]


class DeepToolExecutor:
    def __init__(
        self,
        tools: list[DeepTool],
    ):
        self.tools = {
            tool.name: tool
            for tool in tools
        }

    def execute(
        self,
        tool_name: str,
        arguments: dict,
        confirmed: bool = False,
    ) -> DeepToolResult:
        tool = self.tools.get(tool_name)

        if not tool:
            return DeepToolResult(
                tool_name=tool_name,
                output="",
                success=False,
                error_message=f"工具不存在：{tool_name}",
            )

        if tool.requires_confirmation and not confirmed:
            return DeepToolResult(
                tool_name=tool_name,
                output="",
                success=False,
                error_message=f"工具 {tool_name} 需要人工确认。",
            )

        try:
            output = tool.func(**arguments)

            return DeepToolResult(
                tool_name=tool_name,
                output=output,
                success=True,
            )
        except Exception as exc:
            return DeepToolResult(
                tool_name=tool_name,
                output="",
                success=False,
                error_message=str(exc),
            )