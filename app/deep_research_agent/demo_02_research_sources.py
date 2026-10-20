from dataclasses import asdict

from app.deep_research_agent.sources import ResearchSourceDeduplicator
from app.deep_research_agent.tools import MockEnterpriseKBTool, MockWebSearchTool


def main():
    web_tool = MockWebSearchTool()
    kb_tool = MockEnterpriseKBTool()
    deduplicator = ResearchSourceDeduplicator()

    web_sources = web_tool.search(
        "企业级 AI Agent 平台趋势",
        limit=3,
    )
    kb_sources = kb_tool.search(
        "企业级 AI Agent 平台趋势",
        limit=3,
    )

    sources = deduplicator.deduplicate(
        web_sources + kb_sources
    )

    for source in sources:
        print(asdict(source))
        print("=" * 100)


if __name__ == "__main__":
    main()