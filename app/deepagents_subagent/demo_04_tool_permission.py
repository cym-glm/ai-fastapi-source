from app.deepagents_subagent.tools import (
    SubAgentToolExecutor,
    build_subagent_tools,
)


def main():
    executor = SubAgentToolExecutor(
        build_subagent_tools()
    )

    research_allowed_tools = [
        "search_web",
        "search_enterprise_kb",
    ]

    print("Research Agent 调用 search_web：")
    result = executor.execute(
        tool_name="search_web",
        arguments={
            "query": "AI Agent 平台竞品"
        },
        allowed_tools=research_allowed_tools,
    )
    print(result)

    print("=" * 80)
    print("Research Agent 尝试调用 send_email：")

    try:
        executor.execute(
            tool_name="send_email",
            arguments={
                "to": "boss@example.com",
                "subject": "报告",
                "content": "这是报告。",
            },
            allowed_tools=research_allowed_tools,
        )
    except Exception as exc:
        print("权限拦截：", exc)


if __name__ == "__main__":
    main()