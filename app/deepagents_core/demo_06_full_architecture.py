from app.deepagents_core.service import deep_agent_core_service


def main():
    response = deep_agent_core_service.run_task(
        user_request=(
            "帮我梳理 DeepAgents 核心架构，"
            "要求说明 model、tools、system_prompt、backend、subagents、middleware 的作用。"
        ),
        tenant_id="tenant_001",
        user_id="u_10001",
        thread_id="thread_deep47_full",
    )

    print("thread_id:", response["thread_id"])
    print("task_id:", response["task_id"])

    print("=" * 80)
    print("todos:")
    for todo in response["todos"]:
        print(todo)

    print("=" * 80)
    print("files:")
    for file in response["files"]:
        print("-", file)

    print("=" * 80)
    print("trace:")
    for item in response["trace"]:
        print("-", item)

    print("=" * 80)
    print("final_answer:")
    print(response["final_answer"])


if __name__ == "__main__":
    main()