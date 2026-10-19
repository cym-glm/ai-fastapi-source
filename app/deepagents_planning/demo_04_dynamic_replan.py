from app.deepagents_planning.executor import DeepPlanningExecutor
from app.deepagents_planning.workspace import PlanningWorkspace


def main():
    workspace = PlanningWorkspace(
        "data/deepagents_planning_workspace_demo_04"
    )
    workspace.clear()

    executor = DeepPlanningExecutor(
        workspace=workspace
    )

    result = executor.run_goal(
        "帮我做一个失败测试：调研 DeepAgents Planning，并输出报告。",
        allow_replan=True,
    )

    print("plan_id:", result.plan_id)

    print("=" * 80)
    print("steps:")
    for step in result.steps:
        print(
            step.step_id,
            step.status.value,
            step.title,
            "retry=",
            f"{step.retry_count}/{step.max_retries}",
            "error=",
            step.error_message,
        )

    print("=" * 80)
    print("trace:")
    for item in result.trace:
        print(item.event, item.step_id, item.message)

    print("=" * 80)
    print("files:")
    for file in result.files:
        print(file)


if __name__ == "__main__":
    main()