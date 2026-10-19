from app.deepagents_planning.planner import RuleBasedDeepPlanner
from app.deepagents_planning.schemas import PlanStepStatus


def main():
    planner = RuleBasedDeepPlanner()

    plan = planner.create_plan(
        "帮我做一个失败测试：调研 DeepAgents Planning。"
    )

    step = plan.steps[1]

    print("before:")
    print(step.step_id, step.status.value, step.retry_count, step.max_retries)

    step.status = PlanStepStatus.FAILED
    step.retry_count += 1
    step.error_message = "模拟工具失败"

    if step.retry_count <= step.max_retries:
        step.status = PlanStepStatus.READY
        print("准备重试")
    else:
        print("超过最大重试次数")

    print("after:")
    print(step.step_id, step.status.value, step.retry_count, step.max_retries)


if __name__ == "__main__":
    main()