from app.deepagents_planning.planner import RuleBasedDeepPlanner
from app.deepagents_planning.schemas import PlanStepStatus


def print_steps(title, plan):
    print(title)
    print("=" * 80)

    for step in plan.steps:
        print(step.step_id, step.status.value, step.title)

    print("=" * 120)


def main():
    planner = RuleBasedDeepPlanner()

    plan = planner.create_plan(
        "帮我调研 DeepAgents Planning，并输出一份报告。"
    )

    print_steps("初始状态", plan)

    first_step = planner.next_ready_step(plan)
    first_step.status = PlanStepStatus.SUCCESS
    first_step.result = "目标已明确。"

    planner.refresh_step_status(plan)

    print_steps("第一步完成后", plan)

    second_step = planner.next_ready_step(plan)
    second_step.status = PlanStepStatus.SUCCESS
    second_step.result = "资料已收集。"

    planner.refresh_step_status(plan)

    print_steps("第二步完成后", plan)


if __name__ == "__main__":
    main()