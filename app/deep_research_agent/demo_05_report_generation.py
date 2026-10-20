from app.deep_research_agent.service import deep_research_agent_service
from app.deep_research_agent.schemas import DeepResearchRequest


def main():
    result = deep_research_agent_service.run(
        DeepResearchRequest(
            topic="调研企业级 AI Agent 平台趋势",
            objective="输出一份包含趋势、风险和落地建议的报告",
            user_id="u_10001",
            max_sources=4,
        )
    )

    print(result.final_answer)
    print("=" * 100)
    print("files:")
    for file in result.files:
        print(file)


if __name__ == "__main__":