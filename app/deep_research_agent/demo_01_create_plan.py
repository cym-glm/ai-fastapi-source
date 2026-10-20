from dataclasses import asdict

from app.deep_research_agent.planner import DeepResearchPlanner


def main():
    planner = DeepResearchPlanner()

    plan = planner.create_plan(
        topic="调研企业级 AI Agent 平台的发展趋势",
        objective="输出一份结构化研究报告",
    )

    print(asdict(plan))
    print("=" * 100)
    print(planner.format_plan_markdown(plan))


if __name__ == "__main__":
    main()