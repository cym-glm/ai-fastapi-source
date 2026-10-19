from deepagents import create_deep_agent

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

DEEP_AGENT_PLANNING_PROMPT = """
你是企业级 Deep Research Agent。

工作方式：
1. 遇到复杂任务，必须先制定 Todo List。
2. 每个 Todo 要有明确产物。
3. 不要跳过资料收集直接写结论。
4. 中间结果要写入 workspace。
5. 失败时先重试，再考虑重新规划。
6. 最终输出前必须进行 Review。
"""


agent = create_deep_agent(
    model="openai:gpt-4.1",
    tools=[
        search_enterprise_knowledge_base,
        web_research,
    ],
    system_prompt=DEEP_AGENT_PLANNING_PROMPT,
)


agent.invoke({
    "messages": [
        {"role": "user", "content": "介绍一下 DeepAgents 平台"}
    ]
})