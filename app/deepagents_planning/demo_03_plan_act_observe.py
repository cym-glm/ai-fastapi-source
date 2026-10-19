from app.deepagents_planning.executor import DeepPlanningExecutor
from app.deepagents_planning.workspace import PlanningWorkspace


def main():
    workspace = PlanningWorkspace(
        "data/deepagents_planning_workspace_demo_03"
    )
    workspace.clear()

    executor = DeepPlanningExecutor(
        workspace=workspace
    )

    result = executor.run_goal(
        "帮我调研 DeepAgents Planning，并输出一份结构化报告。",
        allow_replan=True,
    )

    print("plan_id:", result.plan_id)
    print("final_answer:")
    print(result.final_answer)

    print("=" * 80)
    print("files:")
    for file in result.files:
        print(file)

    print("=" * 80)
    print("trace:")
    for item in result.trace:
        print(item.event, item.step_id, item.message)


if __name__ == "__main__":
    main()
