from deepagents import create_deep_agent


def search_enterprise_kb(query: str) -> str:
    """Search enterprise knowledge base."""
    # 这里仅为示意，实际应用中需要调用企业知识库的API
    return "企业知识库检索结果..."


def web_search(query: str) -> str:
    """Search public web information."""
    # 这里仅为示意，实际应用中需要调用搜索引擎的API
    return "外部搜索结果..."


research_agent = {
    "name": "research-agent",
    "description": "负责资料收集和研究笔记整理。",
    "prompt": """
你是 Research Sub-Agent。
你只负责资料收集、事实抽取、来源整理。
不要写最终报告。
输出 Markdown：事实摘要、关键发现、不确定点、来源。
""",
    "tools": [web_search, search_enterprise_kb],
}


reviewer_agent = {
    "name": "reviewer-agent",
    "description": "负责审查研究报告质量、事实依据和遗漏点。",
    "prompt": """
你是 Reviewer Sub-Agent。
你只负责审查，不要重写全文。
输出问题列表、风险点和修改建议。
""",
}


DEEP_RESEARCH_PROMPT = """
你是企业级 Deep Research Agent。

工作方式：
1. 遇到研究任务，先制定计划。
2. 资料收集交给 research-agent。
3. 报告完成后交给 reviewer-agent 审查。
4. 长资料写入 workspace。
5. 主上下文只保留摘要、来源和文件指针。
6. 不要编造没有资料支持的内容。
7. 资料不足时明确说明。
"""


agent = create_deep_agent(
    model="deepseek-chat",
    tools=[web_search, search_enterprise_kb],
    system_prompt=DEEP_RESEARCH_PROMPT,
    subagents=[
        research_agent,
        reviewer_agent,
    ],
)

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "帮我调研企业级 AI Agent 平台的发展趋势，并输出报告。",
        }
    ]
})