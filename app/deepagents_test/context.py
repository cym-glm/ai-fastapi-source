from deepagents import create_deep_agent


CONTEXT_AWARE_PROMPT = """
    你是企业级 Deep Research Agent。

    上下文管理规则：
    1. 不要把长工具结果全部放进最终回答。
    2. 长资料要写入 workspace 文件。
    3. 主 Agent 只保留当前步骤需要的信息。
    4. Sub-Agent 负责隔离重上下文任务。
    5. 最终回答引用文件路径和关键摘要。
    6. 资料不足时必须说明。
    """


agent = create_deep_agent(
    model="openai:gpt-4.1",
    tools=[
        search_enterprise_kb,
        web_search,
    ],
    system_prompt=CONTEXT_AWARE_PROMPT,
)