from app.deepagents_subagent.service import deepagents_subagent_service


def main():
    deepagents_subagent_service.clear_workspace()

    result = deepagents_subagent_service.run_parallel_simulation(
        "对比 Dify、Coze、LangGraph 三个平台，并输出综合分析。"
    )

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