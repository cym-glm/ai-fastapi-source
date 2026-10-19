from app.deepagents_subagent.schemas import SubAgentTool


def search_web(query: str) -> str:
    """
    模拟外部搜索工具。
    """
    return (
        f"外部搜索结果：{query}\n"
        "1. Dify：偏 AI 应用编排和知识库。\n"
        "2. Coze：偏低门槛 Bot 和工作流搭建。\n"
        "3. LangGraph：偏开发者可控 Agent 编排。\n"
        "4. CrewAI：偏角色化 Agent 团队协作。\n"
        "5. AutoGen：偏多 Agent 研究和实验。"
    )


def search_enterprise_kb(query: str) -> str:
    """
    模拟企业知识库检索工具。
    """
    return (
        f"企业知识库检索结果：{query}\n"
        "企业级 Agent 平台通常包含 RAG、Tool Calling、Workflow、"
        "Multi-Agent、权限、日志、评估、部署和可观测性。"
    )


def analyze_text(content: str) -> str:
    """
    模拟文本分析工具。
    """
    return (
        "分析结果：\n"
        "1. AI Agent 平台正在从单点 Chatbot 走向企业级编排平台。\n"
        "2. 核心能力包括 RAG、工具调用、工作流、多 Agent、评估和权限。\n"
        "3. 企业落地更关注稳定性、安全、成本和可观测性。"
    )


def write_markdown_report(title: str, content: str) -> str:
    """
    模拟报告生成工具。
    """
    return f"# {title}\n\n{content}"


def review_content(content: str) -> str:
    """
    模拟内容审查工具。
    """
    checks = []

    if "结论" in content:
        checks.append("包含结论。")
    else:
        checks.append("缺少结论。")

    if "风险" in content:
        checks.append("包含风险分析。")
    else:
        checks.append("建议补充风险分析。")

    if "来源" in content or "资料" in content:
        checks.append("包含资料或来源说明。")
    else:
        checks.append("建议补充资料来源。")

    return "\n".join(f"- {item}" for item in checks)


def inspect_code_repo(query: str) -> str:
    """
    模拟代码仓库分析工具。
    """
    return (
        f"代码仓库分析结果：{query}\n"
        "1. 建议先看 README、package 配置、路由入口和核心 Service。\n"
        "2. 如果是 Agent 项目，重点看 tools、state、graph、memory、retrieval。\n"
        "3. 风险点包括工具权限、状态持久化、异常处理和可观测性。"
    )


def analyze_data(query: str) -> str:
    """
    模拟数据分析工具。
    """
    return (
        f"数据分析结果：{query}\n"
        "1. 需要先明确指标口径。\n"
        "2. 再看趋势、异常值和分组对比。\n"
        "3. 最后输出业务解释和建议。"
    )


def send_email(to: str, subject: str, content: str) -> str:
    """
    模拟高风险写操作。
    """
    return f"已模拟发送邮件给 {to}，主题：{subject}"


def build_subagent_tools() -> list[SubAgentTool]:
    return [
        SubAgentTool(
            name="search_web",
            description="搜索外部资料。",
            func=search_web,
            read_only=True,
        ),
        SubAgentTool(
            name="search_enterprise_kb",
            description="检索企业内部知识库。",
            func=search_enterprise_kb,
            read_only=True,
        ),
        SubAgentTool(
            name="analyze_text",
            description="分析文本内容。",
            func=analyze_text,
            read_only=True,
        ),
        SubAgentTool(
            name="write_markdown_report",
            description="生成 Markdown 报告。",
            func=write_markdown_report,
            read_only=False,
        ),
        SubAgentTool(
            name="review_content",
            description="审查内容质量。",
            func=review_content,
            read_only=True,
        ),
        SubAgentTool(
            name="inspect_code_repo",
            description="分析代码仓库结构。",
            func=inspect_code_repo,
            read_only=True,
        ),
        SubAgentTool(
            name="analyze_data",
            description="分析数据指标。",
            func=analyze_data,
            read_only=True,
        ),
        SubAgentTool(
            name="send_email",
            description="发送邮件，高风险写操作。",
            func=send_email,
            read_only=False,
            requires_confirmation=True,
        ),
    ]


class SubAgentToolExecutor:
    def __init__(
        self,
        tools: list[SubAgentTool],
    ):
        self.tools = {
            tool.name: tool
            for tool in tools
        }

    def execute(
        self,
        tool_name: str,
        arguments: dict,
        allowed_tools: list[str],
        confirmed: bool = False,
    ) -> str:
        if tool_name not in allowed_tools:
            raise PermissionError(
                f"当前 Sub-Agent 无权使用工具：{tool_name}"
            )

        tool = self.tools.get(tool_name)

        if not tool:
            raise ValueError(
                f"工具不存在：{tool_name}"
            )

        if tool.requires_confirmation and not confirmed:
            raise PermissionError(
                f"工具 {tool_name} 需要人工确认。"
            )

        return tool.func(**arguments)