import uuid
from dataclasses import asdict

from app.deep_research_agent.context import DeepResearchContextManager
from app.deep_research_agent.planner import DeepResearchPlanner
from app.deep_research_agent.report import DeepResearchReportBuilder
from app.deep_research_agent.schemas import (
    DeepResearchRequest,
    DeepResearchResult,
    ResearchTaskStatus,
    ResearchStepStatus,
)
from app.deep_research_agent.sources import ResearchSourceDeduplicator
from app.deep_research_agent.subagents import (
    AnalysisSubAgent,
    ResearchSubAgent,
    ReviewerSubAgent,
    WriterSubAgent,
)
from app.deep_research_agent.tools import (
    MockEnterpriseKBTool,
    MockWebSearchTool,
)
from app.deep_research_agent.workspace import DeepResearchWorkspace


class DeepResearchAgentService:
    def __init__(self):
        self.workspace = DeepResearchWorkspace()
        self.planner = DeepResearchPlanner()
        self.web_tool = MockWebSearchTool()
        self.kb_tool = MockEnterpriseKBTool()
        self.deduplicator = ResearchSourceDeduplicator()
        self.research_agent = ResearchSubAgent()
        self.analysis_agent = AnalysisSubAgent()
        self.writer_agent = WriterSubAgent()
        self.reviewer_agent = ReviewerSubAgent()
        self.context_manager = DeepResearchContextManager()
        self.report_builder = DeepResearchReportBuilder()

    def run(
        self,
        request: DeepResearchRequest,
    ) -> DeepResearchResult:
        task_id = f"research_task_{uuid.uuid4().hex[:12]}"
        thread_id = f"research_thread_{uuid.uuid4().hex[:12]}"
        trace: list[str] = []

        try:
            self.workspace.clear()

            trace.append(f"创建研究任务：{task_id}")
            trace.append(f"thread_id：{thread_id}")

            status = ResearchTaskStatus.PLANNING

            plan = self.planner.create_plan(
                topic=request.topic,
                objective=request.objective,
            )
            self.workspace.write_file(
                "/plan/research_plan.md",
                self.planner.format_plan_markdown(plan),
            )
            trace.append("已生成 ResearchPlan，并写入 /plan/research_plan.md")

            self._mark_step(plan, "step_001", ResearchStepStatus.SUCCESS, "研究目标已明确。")

            status = ResearchTaskStatus.RESEARCHING
            trace.append("开始资料收集")

            web_sources = []
            kb_sources = []

            if request.include_web:
                web_sources = self.web_tool.search(
                    query=request.topic,
                    limit=request.max_sources,
                )
                trace.append(f"外部搜索返回 {len(web_sources)} 条资料")

            if request.include_enterprise_kb:
                kb_sources = self.kb_tool.search(
                    query=request.topic,
                    limit=request.max_sources,
                )
                trace.append(f"企业知识库返回 {len(kb_sources)} 条资料")

            sources = self.deduplicator.deduplicate(
                web_sources + kb_sources
            )

            research_note = self.research_agent.run(
                topic=request.topic,
                web_sources=web_sources,
                kb_sources=kb_sources,
                write_file=self.workspace.write_file,
            )
            self._mark_step(
                plan,
                "step_002",
                ResearchStepStatus.SUCCESS,
                "Research Sub-Agent 已完成资料收集。",
            )
            trace.append("Research Sub-Agent 已输出 /research/research_notes.md")

            status = ResearchTaskStatus.ANALYZING

            analysis_result = self.analysis_agent.run(
                research_note=research_note,
                write_file=self.workspace.write_file,
            )
            self._mark_step(
                plan,
                "step_003",
                ResearchStepStatus.SUCCESS,
                "Analysis Sub-Agent 已完成结构化分析。",
            )
            trace.append("Analysis Sub-Agent 已输出 /analysis/analysis_notes.md")

            status = ResearchTaskStatus.WRITING

            writer_context = self.context_manager.build_writer_context(
                plan=plan,
                research_note=research_note,
                analysis_result=analysis_result,
            )
            self.workspace.write_file(
                "/context/writer_context.md",
                writer_context,
            )
            trace.append("已构建 writer context pack，并写入 /context/writer_context.md")

            draft_file = self.writer_agent.write_draft(
                topic=request.topic,
                objective=request.objective,
                research_note=research_note,
                analysis_result=analysis_result,
                write_file=self.workspace.write_file,
            )
            draft = self.workspace.read_file(draft_file)
            self._mark_step(
                plan,
                "step_004",
                ResearchStepStatus.SUCCESS,
                "Writer Sub-Agent 已完成报告草稿。",
            )
            trace.append("Writer Sub-Agent 已输出 /reports/draft_report.md")

            status = ResearchTaskStatus.REVIEWING

            review = self.reviewer_agent.run(
                draft=draft,
                write_file=self.workspace.write_file,
            )
            self._mark_step(
                plan,
                "step_005",
                ResearchStepStatus.SUCCESS,
                "Reviewer Sub-Agent 已完成报告审查。",
            )
            trace.append("Reviewer Sub-Agent 已输出 /reports/review_notes.md")

            final_report = self.writer_agent.write_final(
                draft=draft,
                review=review,
                write_file=self.workspace.write_file,
            )
            self._mark_step(
                plan,
                "step_006",
                ResearchStepStatus.SUCCESS,
                "已输出最终报告。",
            )
            trace.append("最终报告已写入 /reports/final_report.md")

            self.workspace.write_file(
                "/plan/research_plan.md",
                self.planner.format_plan_markdown(plan),
            )
            self.workspace.write_file(
                "/reports/sources.md",
                self.report_builder.build_sources_section(sources),
            )
            self.workspace.write_file(
                "/reports/task_summary.md",
                self.report_builder.build_task_summary(plan, review),
            )

            status = ResearchTaskStatus.COMPLETED

            final_answer = self.context_manager.build_final_summary(
                final_report=final_report,
            )

            return DeepResearchResult(
                task_id=task_id,
                thread_id=thread_id,
                status=status,
                topic=request.topic,
                plan=plan,
                final_answer=final_answer,
                sources=sources,
                files=self.workspace.list_files(),
                trace=trace,
                review=review,
            )

        except Exception as exc:
            trace.append(f"任务失败：{exc}")

            fallback_plan = self.planner.create_plan(
                topic=request.topic,
                objective=request.objective,
            )

            return DeepResearchResult(
                task_id=task_id,
                thread_id=thread_id,
                status=ResearchTaskStatus.FAILED,
                topic=request.topic,
                plan=fallback_plan,
                final_answer="Deep Research Agent 执行失败。",
                sources=[],
                files=self.workspace.list_files(),
                trace=trace,
                review=None,
                error_message=str(exc),
            )

    def read_file(
        self,
        file_path: str,
    ) -> str:
        return self.workspace.read_file(file_path)

    def list_files(self) -> list[str]:
        return self.workspace.list_files()

    def clear_workspace(self) -> None:
        self.workspace.clear()

    def _mark_step(
        self,
        plan,
        step_id: str,
        status: ResearchStepStatus,
        result_summary: str,
    ) -> None:
        for step in plan.steps:
            if step.step_id == step_id:
                step.status = status
                step.result_summary = result_summary
                return

    def result_to_dict(
        self,
        result: DeepResearchResult,
    ) -> dict:
        return asdict(result)


deep_research_agent_service = DeepResearchAgentService()