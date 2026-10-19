from deepagents import create_deep_agent


# 定义工具函数
def search_enterprise_kb(query: str) -> str:
    """Search enterprise knowledge base."""
    # 这里仅为示例，实际应用中需要调用企业知识库的API
    return "企业知识库检索结果..."


def web_search(query: str) -> str:
    """Search public web information."""
    # 这里仅为示例，实际应用中需要调用外部搜索引擎API
    return "外部搜索结果..."


research_agent = {
    "name": "research-agent",
    "description": "负责资料收集和研究笔记整理。",
    "prompt": """
        你是 Research Sub-Agent。
        你只负责收集资料和整理事实。
        不要写最终报告。
        输出 Markdown，包含事实摘要、关键发现、不确定点。
    """,
    "tools": [search_enterprise_kb, web_search],
}

reviewer_agent = {
    "name": "reviewer-agent",
    "description": "负责审查报告质量、事实依据和遗漏点。",
    "prompt": """
        你是 Reviewer Sub-Agent。
        你只负责审查，不要重写全文。
        输出问题列表、风险点和修改建议。
    """,
}

agent = create_deep_agent(
    model="openai:gpt-4.1",
    tools=[search_enterprise_kb, web_search],
    system_prompt="""
        你是企业 Deep Research Agent。
        复杂任务要先规划，再委派 subagents。
        不要把所有调研细节放在主上下文里。
    """,
    subagents=[
        research_agent,
        reviewer_agent,
    ],
)