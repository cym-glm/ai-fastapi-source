from app.deepagents_core.tools import (
    DeepToolExecutor,
    build_default_tools,
)


def main():
    executor = DeepToolExecutor(
        build_default_tools()
    )

    result = executor.execute(
        "search_enterprise_knowledge_base",
        {
            "query": "DeepAgents 适合什么复杂任务？"
        },
    )

    print("search result:")
    print(result)

    print("=" * 80)

    email_result = executor.execute(
        "send_email",
        {
            "to": "test@example.com",
            "subject": "DeepAgents 报告",
            "content": "这里是报告内容。",
        },
        confirmed=False,
    )

    print("email without confirmation:")
    print(email_result)

    print("=" * 80)

    email_confirmed = executor.execute(
        "send_email",
        {
            "to": "test@example.com",
            "subject": "DeepAgents 报告",
            "content": "这里是报告内容。",
        },
        confirmed=True,
    )

    print("email with confirmation:")
    print(email_confirmed)


if __name__ == "__main__":
    main()