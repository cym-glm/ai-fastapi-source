from app.deep_research_agent.schemas import (
    AnalysisResult,
    ResearchNote,
    ResearchPlan,
)


class DeepResearchContextManager:
    """
    项目四教学版 Context Manager。

    目标：
    1. 不把所有 source content 都塞进最终 prompt。
    2. 只构造报告生成需要的摘要上下文。
    3. 保留文件指针，方便追溯。
    """

    def build_writer_context(
        self,
        plan: ResearchPlan,
        research_note: ResearchNote,
        analysis_result: AnalysisResult,
    ) -> str:
        source_summary = "\n".join(
            f"- {source.title}｜type={source.source_type.value}｜score={source.score}"
            for source in research_note.sources[:8]
        )

        key_points = "\n".join(
            f"- {item}"
            for item in research_note.key_points
        )

        findings = "\n".join(
            f"- {item}"
            for item in analysis_result.findings
        )

        risks = "\n".join(
            f"- {item}"
            for item in analysis_result.risks
        )

        return f"""
# Writer Context Pack

## Topic

{plan.topic}

## Objective

{plan.objective}

## Research Key Points

{key_points}

## Analysis Findings

{findings}

## Risks

{risks}

## Source Pointers

{source_summary}

## Workspace Files

- research_notes: {research_note.output_file}
- analysis_notes: {analysis_result.output_file}
""".strip()

    def build_final_summary(
        self,
        final_report: str,
        max_chars: int = 1200,
    ) -> str:
        if len(final_report) <= max_chars:
            return final_report

        return final_report[:max_chars] + "\n\n...【报告已截断，完整内容请查看 /reports/final_report.md】"