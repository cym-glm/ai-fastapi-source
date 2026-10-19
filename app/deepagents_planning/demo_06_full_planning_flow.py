from app.deepagents_planning.service import deepagents_planning_service


def main():
    deepagents_planning_service.clear_workspace()

    result = deepagents_planning_service.run_goal(
        user_goal=(
            "帮我调研 DeepAgents Planning 的设计思路，"
            "要求输出包含任务拆解、Todo、Plan-Act-Observe、失败重试、动态 Replan 的报告。"
        ),
        allow_replan=True,
    )

    print("plan_id:", result["plan_id"])
    print("user_goal:", result["user_goal"])

    print("=" * 80)
    print("steps:")
    for step in result["steps"]:
        print(
            step["step_id"],
            step["status"],
            step["title"],
            "output_file=",
            step["output_file"],
        )

    print("=" * 80)
    print("files:")
    for file in result["files"]:
        print(file)

    print("=" * 80)
    print("trace:")
    for item in result["trace"]:
        print(item["event"], item["step_id"], item["message"])

    print("=" * 80)
    print("final_answer:")
    print(result["final_answer"])


if __name__ == "__main__":
    main()