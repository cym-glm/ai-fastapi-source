from app.deepagents_intro.deep_agent import TeachingDeepAgent


def main():
    agent = TeachingDeepAgent(
        workspace_dir="data/deep_agent_workspace_full"
    )

    result = agent.run(
        "帮我调研一下 AI Agent 平台竞品，并输出一份结构化报告。"
    )

    print("task_id:", result.task_id)
    print("goal:", result.goal)

    print("=" * 80)
    print("trace:")
    for item in result.trace:
        print("-", item)

    print("=" * 80)
    print("todos:")
    for todo in result.todos:
        print(todo.todo_id, todo.status.value, todo.title, todo.result)

    print("=" * 80)
    print("workspace_files:")
    for file in result.workspace_files:
        print("-", file)

    print("=" * 80)
    print("final_answer:")
    print(result.final_answer)


if __name__ == "__main__":
    main()