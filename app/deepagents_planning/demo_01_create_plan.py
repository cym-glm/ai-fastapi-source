from dataclasses import asdict

from app.deepagents_planning.planner import RuleBasedDeepPlanner


def main():
    planner = RuleBasedDeepPlanner()

    plan = planner.create_plan(
        "帮我调研 AI Agent 平台竞品，并输出一份结构化分析报告。"
    )

    print("plan_id:", plan.plan_id)
    print("task_type:", plan.task_type.value)
    print("user_goal:", plan.user_goal)
    print("=" * 80)

    for step in plan.steps:
        print(asdict(step))
        print("-" * 80)


if __name__ == "__main__":
    main()