from app.deepagents_intro.deep_agent import (
    AnalysisSubAgent,
    ResearchSubAgent,
    WriterSubAgent,
)


def main():
    research_agent = ResearchSubAgent()
    analysis_agent = AnalysisSubAgent()
    writer_agent = WriterSubAgent()

    research_result = research_agent.run(
        "AI Agent 平台 竞品 调研"
    )

    analysis_result = analysis_agent.run(
        task="分析 AI Agent 平台趋势",
        content=research_result.result,
    )

    writer_result = writer_agent.run(
        task="输出 AI Agent 平台竞品调研报告",
        research_notes=research_result.result,
        analysis_notes=analysis_result.result,
    )

    print("research:")
    print(research_result.result)

    print("=" * 80)
    print("analysis:")
    print(analysis_result.result)

    print("=" * 80)
    print("report:")
    print(writer_result.result)


if __name__ == "__main__":
    main()