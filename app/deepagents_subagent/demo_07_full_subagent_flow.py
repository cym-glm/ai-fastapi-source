from app.deepagents_subagent.service import deepagents_subagent_service


def main():
    deepagents_subagent_service.clear_workspace()

    result = deepagents_subagent_service.run(
        "帮我调研 AI Agent 平台竞品，分析产品能力、目标用户、企业落地风险，并输出一份报告。"
    )

    print("1. 子 Agent 列表")
    for spec in deepagents_subagent_service.list_subagents():
        print(spec["name"], spec["role"], spec["allowed_tools"])

    print("=" * 120)
    print("2. Trace")
    for item in result["trace"]:
        print("-", item)

    print("=" * 120)
    print("3. 子任务结果")
    for item in result["delegation_results"]:
        print("agent:", item["agent_name"])
        print("role:", item["role"])
        print("status:", item["status"])
        print("summary:", item["summary"])
        print("output_file:", item["output_file"])
        print("-" * 80)

    print("=" * 120)
    print("4. Workspace Files")
    for file in result["files"]:
        print(file)

    print("=" * 120)
    print("5. Final Answer")
    print(result["final_answer"])


if __name__ == "__main__":
    main()