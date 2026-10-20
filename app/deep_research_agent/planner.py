import uuid

from app.deep_research_agent.schemas import (
    ResearchPlan,
    ResearchPlanStep,
    ResearchStepStatus,
    ResearchSubAgentRole,
)


class DeepResearchPlanner:
    def create_plan(
        self,
        topic: str,
        objective: str,
    ) -> ResearchPlan:
        dimensions = self._extract_dimensions(topic)

        steps = [
            ResearchPlanStep(
                step_id="step_001",
                title="明确研究目标",
                description="确认研究主题、研究目标、输出格式和分析维度。",
                owner=None,
                status=ResearchStepStatus.PENDING,
                output_file="/plan/task_brief.md",
            ),
            ResearchPlanStep(
                step_id="step_002",
                title="收集研究资料",
                description="调用外部搜索和企业知识库，收集相关资料。",
                owner=ResearchSubAgentRole.RESEARCHER,
                status=ResearchStepStatus.PENDING,
                output_file="/research/research_notes.md",
            ),
            ResearchPlanStep(
                step_id="step_003",
                title="结构化分析",
                description="基于资料分析趋势、机会、风险和落地建议。",
                owner=ResearchSubAgentRole.ANALYST,
                status=ResearchStepStatus.PENDING,
                output_file="/analysis/analysis_notes.md",
            ),
            ResearchPlanStep(
                step_id="step_004",
                title="生成报告草稿",
                description="根据研究笔记和分析结论生成结构化报告草稿。",
                owner=ResearchSubAgentRole.WRITER,
                status=ResearchStepStatus.PENDING,
                output_file="/reports/draft_report.md",
            ),
            ResearchPlanStep(
                step_id="step_005",
                title="审查报告质量",
                description="检查报告是否覆盖研究目标、来源、风险和建议。",
                owner=ResearchSubAgentRole.REVIEWER,
                status=ResearchStepStatus.PENDING,
                output_file="/reports/review_notes.md",
            ),
            ResearchPlanStep(
                step_id="step_006",
                title="输出最终报告",
                description="结合审查意见输出最终研究报告。",
                owner=ResearchSubAgentRole.WRITER,
                status=ResearchStepStatus.PENDING,
                output_file="/reports/final_report.md",
            ),
        ]

        return ResearchPlan(
            plan_id=f"research_plan_{uuid.uuid4().hex[:12]}",
            topic=topic,
            objective=objective,
            dimensions=dimensions,
            steps=steps,
        )

    def format_plan_markdown(
        self,
        plan: ResearchPlan,
    ) -> str:
        lines = [
            "# Deep Research Plan",
            "",
            f"Plan ID：{plan.plan_id}",
            f"Topic：{plan.topic}",
            f"Objective：{plan.objective}",
            "",
            "## 研究维度",
        ]

        for dimension in plan.dimensions:
            lines.append(f"- {dimension}")

        lines.extend([
            "",
            "## 执行步骤",
        ])

        for step in plan.steps:
            lines.extend([
                "",
                f"### {step.step_id}｜{step.title}",
                f"- owner：{step.owner.value if step.owner else 'main-agent'}",
                f"- status：{step.status.value}",
                f"- output_file：{step.output_file}",
                f"- description：{step.description}",
            ])

        return "\n".join(lines)

    def _extract_dimensions(
        self,
        topic: str,
    ) -> list[str]:
        default_dimensions = [
            "产品能力",
            "技术架构",
            "目标用户",
            "商业模式",
            "企业落地风险",
            "未来趋势",
        ]

        custom_dimensions = []

        for item in default_dimensions:
            if item in topic:
                custom_dimensions.append(item)

        if custom_dimensions:
            return custom_dimensions

        return default_dimensions