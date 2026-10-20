from app.deep_research_agent.schemas import (
    ResearchPlan,
    ResearchSource,
    ReviewResult,
)


class DeepResearchReportBuilder:
    def build_sources_section(
        self,
        sources: list[ResearchSource],
    ) -> str:
        lines = [
            "## Sources",
            "",
        ]

        for index, source in enumerate(sources, start=1):
            lines.extend([
                f"{index}. {source.title}",
                f"   - type: {source.source_type.value}",
                f"   - score: {source.score}",
                f"   - url: {source.url or ''}",
                f"   - file_path: {source.file_path or ''}",
                "",
            ])

        return "\n".join(lines)

    def build_task_summary(
        self,
        plan: ResearchPlan,
        review: ReviewResult | None,
    ) -> str:
        review_status = "未审查"

        if review:
            review_status = "通过" if review.passed else "未通过"

        return f"""
# Research Task Summary

- plan_id：{plan.plan_id}
- topic：{plan.topic}
- objective：{plan.objective}
- dimensions：{", ".join(plan.dimensions)}
- review_status：{review_status}
""".strip()