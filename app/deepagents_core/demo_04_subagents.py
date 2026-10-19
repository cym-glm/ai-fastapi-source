from app.deepagents_core.subagents import (
    TeachingSubAgentRunner,
    build_default_subagents,
)


def main():
    runner = TeachingSubAgentRunner(
        build_default_subagents()
    )

    tasks = [
        ("research-agent", "调研 DeepAgents 核心架构"),
        ("writer-agent", "根据资料写一份报告草稿"),
        ("reviewer-agent", "检查报告是否完整"),
    ]

    for name, task in tasks:
        result = runner.run(
            name=name,
            task=task,
        )

        print("subagent:", result.name)
        print("task:", result.task)
        print("success:", result.success)
        print("result:")
        print(result.result)
        print("=" * 80)


if __name__ == "__main__":
    main()