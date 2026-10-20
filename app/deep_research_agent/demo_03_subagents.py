from dataclasses import asdict

from app.deep_research_agent.subagents import (
    AnalysisSubAgent,
    ResearchSubAgent,
    ReviewerSubAgent,
    WriterSubAgent,
)
from app.deep_research_agent.tools import MockEnterpriseKBTool, MockWebSearchTool
from app.deep_research_agent.workspace import DeepResearchWorkspace


def main():
    workspace = DeepResearchWorkspace(
        "data/deep_research_workspace_demo_03"
    )
    workspace.clear()

    topic = "企业级 AI Agent 平台趋势"

    web_sources = MockWebSearchTool().search(topic, limit=2)
    kb_sources = MockEnterpriseKBTool().search(topic, limit=2)

    research_note = ResearchSubAgent().run(
        topic=topic,
        web_sources=web_sources,
        kb_sources=kb_sources,
        write_file=workspace.write_file,
    )

    analysis = AnalysisSubAgent().run(
        research_note=research_note,
        write_file=workspace.write_file,
    )

    draft_file = WriterSubAgent().write_draft(
        topic=topic,
        objective="输出研究报告",
        research_note=research_note,
        analysis_result=analysis,
        write_file=workspace.write_file,
    )

    draft = workspace.read_file(draft_file)

    review = ReviewerSubAgent().run(
        draft=draft,
        write_file=workspace.write_file,
    )

    print("research_note:")
    print(asdict(research_note))

    print("=" * 100)
    print("analysis:")
    print(asdict(analysis))

    print("=" * 100)
    print("review:")
    print(asdict(review))

    print("=" * 100)
    print("files:")
    for file in workspace.list_files():
        print(file)


if __name__ == "__main__":
    main()