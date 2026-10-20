from app.deep_research_agent.context import DeepResearchContextManager
from app.deep_research_agent.planner import DeepResearchPlanner
from app.deep_research_agent.subagents import AnalysisSubAgent, ResearchSubAgent
from app.deep_research_agent.tools import MockEnterpriseKBTool, MockWebSearchTool
from app.deep_research_agent.workspace import DeepResearchWorkspace


def main():
    workspace = DeepResearchWorkspace(
        "data/deep_research_workspace_demo_04"
    )
    workspace.clear()

    topic = "Deep Research Agent 架构设计"
    planner = DeepResearchPlanner()
    plan = planner.create_plan(topic, "输出架构设计报告")

    research_note = ResearchSubAgent().run(
        topic=topic,
        web_sources=MockWebSearchTool().search(topic, limit=2),
        kb_sources=MockEnterpriseKBTool().search(topic, limit=2),
        write_file=workspace.write_file,
    )

    analysis = AnalysisSubAgent().run(
        research_note=research_note,
        write_file=workspace.write_file,
    )

    context = DeepResearchContextManager().build_writer_context(
        plan=plan,
        research_note=research_note,
        analysis_result=analysis,
    )

    workspace.write_file(
        "/context/writer_context.md",
        context,
    )

    print(context)


if __name__ == "__main__":
    main()