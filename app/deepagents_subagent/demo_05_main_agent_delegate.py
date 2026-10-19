from app.deepagents_subagent.service import deepagents_subagent_service


def main():
    deepagents_subagent_service.clear_workspace()

    result = deepagents_subagent_service.run(
        "帮我调研 AI Agent 平台竞品，分析趋势，并输出一份结构化报告。"
    )

    print("user_goal:", result["user_goal"])

    print("=" * 80)
    print("trace:")
    for item in result["trace"]:
        print("-", item)

    print("=" * 80)
    print("delegation_results:")
    for item in result["delegation_results"]:
        print(item["agent_name"], item["status"], item["summary"])

    print("=" * 80)
    print("files:")
    for file in result["files"]:
        print(file)

    print("=" * 80)
    print("final_answer:")
    print(result["final_answer"])


if __name__ == "__main__":
    main()