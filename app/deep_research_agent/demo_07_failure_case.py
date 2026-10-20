from app.deep_research_agent.schemas import DeepResearchRequest
from app.deep_research_agent.service import deep_research_agent_service


def main():
    # 教学版：关闭 web 和企业知识库，模拟资料不足。
    result = deep_research_agent_service.run(
        DeepResearchRequest(
            topic="一个完全没有资料来源的未知研究主题",
            objective="输出研究报告",
            include_web=False,
            include_enterprise_kb=False,
        )
    )

    print("status:", result.status.value)
    print("sources:", len(result.sources))
    print("trace:")
    for item in result.trace:
        print("-", item)

    print("=" * 100)
    print(result.final_answer)


if __name__ == "__main__":
    main()