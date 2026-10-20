from dataclasses import asdict

from app.deep_research_agent.schemas import DeepResearchRequest
from app.deep_research_agent.service import deep_research_agent_service


def main():
    result = deep_research_agent_service.run(
        DeepResearchRequest(
            topic=(
                "调研 2026 年企业级 AI Agent 平台的发展趋势，"
                "重点分析产品能力、技术架构、目标用户、商业模式和落地风险。"
            ),
            objective="输出一份结构化 Deep Research 报告",
            tenant_id="tenant_001",
            user_id="u_10001",
            max_sources=5,
        )
    )

    print("task_id:", result.task_id)
    print("thread_id:", result.thread_id)
    print("status:", result.status.value)

    print("=" * 100)
    print("plan:")
    print(asdict(result.plan))

    print("=" * 100)
    print("trace:")
    for item in result.trace:
        print("-", item)

    print("=" * 100)
    print("sources:")
    for source in result.sources:
        print(source.title, source.source_type.value, source.score)

    print("=" * 100)
    print("files:")
    for file in result.files:
        print(file)

    print("=" * 100)
    print("review:")
    print(asdict(result.review) if result.review else None)

    print("=" * 100)
    print("final_answer:")
    print(result.final_answer)


if __name__ == "__main__":
    main()