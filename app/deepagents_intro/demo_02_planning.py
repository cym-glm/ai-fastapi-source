from app.deepagents_intro.deep_agent import TeachingDeepAgent


def main():
    agent = TeachingDeepAgent()
    task = agent.create_task(
        "帮我调研一下 AI Agent 平台竞品，并输出一份结构化报告。"
    )

    todos = agent.plan(task)

    print("task_id:", task.task_id)
    print("goal:", task.goal)
    print("=" * 80)

    for todo in todos:
        print(todo.todo_id, todo.status.value, todo.title)


if __name__ == "__main__":
    main()