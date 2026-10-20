import uuid

from app.deep_research_agent.schemas import (
    AnalysisResult,
    ResearchNote,
    ResearchSource,
    ReviewResult,
)


class ResearchSubAgent:
    def run(
        self,
        topic: str,
        web_sources: list[ResearchSource],
        kb_sources: list[ResearchSource],
        write_file,
    ) -> ResearchNote:
        sources = web_sources + kb_sources

        key_points = [
            "AI Agent 平台正在从单点 Chatbot 走向企业级可编排平台。",
            "Deep Research 类任务需要 Planning、Sub-Agent、Workspace 和 Context 管理。",
            "企业落地重点不是模型本身，而是权限、数据、工具、安全、评估和可观测性。",
            "RAG 可以为 DeepAgent 提供企业内部知识，Sub-Agent 可以隔离复杂研究上下文。",
        ]

        content = [
            "# Research Notes",
            "",
            f"研究主题：{topic}",
            "",
            "## 关键发现",
        ]

        for point in key_points:
            content.append(f"- {point}")

        content.extend([
            "",
            "## Sources",
        ])

        for source in sources:
            content.extend([
                "",
                f"### {source.title}",
                f"- type：{source.source_type.value}",
                f"- score：{source.score}",
                f"- url：{source.url or ''}",
                f"- file_path：{source.file_path or ''}",
                "",
                source.content,
            ])

        output_file = "/research/research_notes.md"
        write_file(output_file, "\n".join(content))

        return ResearchNote(
            note_id=f"research_note_{uuid.uuid4().hex[:10]}",
            topic=topic,
            key_points=key_points,
            sources=sources,
            output_file=output_file,
        )


class AnalysisSubAgent:
    def run(
        self,
        research_note: ResearchNote,
        write_file,
    ) -> AnalysisResult:
        findings = [
            "AI Agent 平台的竞争点正在从模型接入转向任务编排、工具生态、企业数据集成和评估闭环。",
            "Deep Research Agent 适合处理资料来源多、步骤长、需要反复分析和写作的任务。",
            "企业级 Agent 项目必须把 Planning、Context 管理、权限、Trace、Evaluation 放进架构设计。",
        ]

        risks = [
            "上下文管理不当会导致成本高、速度慢、输出不稳定。",
            "Sub-Agent 权限过大可能带来数据泄露或误操作风险。",
            "资料来源缺少引用会降低报告可信度。",
            "没有 Evaluation 会导致系统只能靠主观感觉优化。",
        ]

        opportunities = [
            "企业知识库 + Deep Research 可以形成内部咨询助手。",
            "结合 RAG 和 Sub-Agent 可以降低长任务上下文压力。",
            "通过 Query Log、Trace 和 Review 可以形成持续优化闭环。",
        ]

        recommendations = [
            "先从企业内部知识库和研究报告生成场景落地。",
            "把 Research、Analysis、Writer、Reviewer 拆成独立 Sub-Agent。",
            "长内容写入 Workspace，只把摘要和文件指针放入主上下文。",
            "高风险工具必须加入人工确认和审计。",
        ]

        lines = [
            "# Analysis Notes",
            "",
            "## Findings",
            *[f"- {item}" for item in findings],
            "",
            "## Risks",
            *[f"- {item}" for item in risks],
            "",
            "## Opportunities",
            *[f"- {item}" for item in opportunities],
            "",
            "## Recommendations",
            *[f"- {item}" for item in recommendations],
        ]

        output_file = "/analysis/analysis_notes.md"
        write_file(output_file, "\n".join(lines))

        return AnalysisResult(
            analysis_id=f"analysis_{uuid.uuid4().hex[:10]}",
            findings=findings,
            risks=risks,
            opportunities=opportunities,
            recommendations=recommendations,
            output_file=output_file,
        )


class WriterSubAgent:
    def write_draft(
        self,
        topic: str,
        objective: str,
        research_note: ResearchNote,
        analysis_result: AnalysisResult,
        write_file,
    ) -> str:
        sources_text = "\n".join(
            f"- {source.title}（{source.source_type.value}，score={source.score}）"
            for source in research_note.sources
        )

        content = f"""
# Deep Research Report Draft

## 一、研究主题

{topic}

## 二、研究目标

{objective}

## 三、核心结论

{self._format_list(analysis_result.findings)}

## 四、机会点

{self._format_list(analysis_result.opportunities)}

## 五、主要风险

{self._format_list(analysis_result.risks)}

## 六、落地建议

{self._format_list(analysis_result.recommendations)}

## 七、参考来源

{sources_text}
""".strip()

        output_file = "/reports/draft_report.md"
        write_file(output_file, content)

        return output_file

    def write_final(
        self,
        draft: str,
        review: ReviewResult,
        write_file,
    ) -> str:
        review_text = "\n".join(
            f"- {item}"
            for item in review.suggestions
        )

        final_report = f"""
{draft}

## 八、Review 后补充

{review_text}

## 九、最终说明

本报告由 Deep Research Agent 自动完成，包含任务规划、资料收集、结构化分析、报告生成和审查流程。实际生产环境中，外部资料和企业知识库资料都应返回真实来源链接、文档 ID、chunk ID 和检索分数。
""".strip()

        output_file = "/reports/final_report.md"
        write_file(output_file, final_report)

        return final_report

    def _format_list(
        self,
        items: list[str],
    ) -> str:
        return "\n".join(
            f"- {item}"
            for item in items
        )


class ReviewerSubAgent:
    def run(
        self,
        draft: str,
        write_file,
    ) -> ReviewResult:
        issues: list[str] = []
        suggestions: list[str] = []

        if "核心结论" not in draft:
            issues.append("报告缺少核心结论。")
            suggestions.append("补充核心结论章节。")

        if "主要风险" not in draft:
            issues.append("报告缺少风险分析。")
            suggestions.append("补充企业落地风险。")

        if "参考来源" not in draft:
            issues.append("报告缺少参考来源。")
            suggestions.append("补充来源列表。")

        if not issues:
            suggestions.extend([
                "报告结构完整，可以补充更多真实来源链接。",
                "建议在生产环境加入 citation 校验。",
                "建议把 Review 结果保存到任务日志，便于后续评估。",
            ])

        passed = len(issues) == 0

        content = [
            "# Review Notes",
            "",
            f"passed：{passed}",
            "",
            "## Issues",
            *[f"- {item}" for item in issues],
            "",
            "## Suggestions",
            *[f"- {item}" for item in suggestions],
        ]

        output_file = "/reports/review_notes.md"
        write_file(output_file, "\n".join(content))

        return ReviewResult(
            review_id=f"review_{uuid.uuid4().hex[:10]}",
            passed=passed,
            issues=issues,
            suggestions=suggestions,
            output_file=output_file,
        )