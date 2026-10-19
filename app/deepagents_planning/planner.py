import uuid

from app.deepagents_planning.schemas import (
    DeepPlan,
    PlanStep,
    PlanStepStatus,
    PlanStepType,
    PlanningTaskType,
)

# 用户目标 ---  llm 结构化输出 ---  deep paln 执行计划
class RuleBasedDeepPlanner:
    """
    教学版 Planner。

    生产环境可以替换成 LLM + Structured Output。
    """

    def create_plan(
        self,
        user_goal: str,
    ) -> DeepPlan:
        task_type = self._classify_task(user_goal)

        if task_type in [
            PlanningTaskType.RESEARCH,
            PlanningTaskType.REPORT,
        ]:
            steps = self._create_research_report_steps(user_goal)

        elif task_type == PlanningTaskType.CODE_ANALYSIS:
            steps = self._create_code_analysis_steps(user_goal)

        elif task_type == PlanningTaskType.DATA_ANALYSIS:
            steps = self._create_data_analysis_steps(user_goal)

        else:
            steps = self._create_general_steps(user_goal)

        plan = DeepPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:12]}",
            task_type=task_type,
            user_goal=user_goal,
            steps=steps,
            summary=f"针对任务「{user_goal}」生成执行计划。",
        )

        self.refresh_step_status(plan)

        return plan

    def refresh_step_status(
        self,
        plan: DeepPlan,
    ) -> None:
        success_ids = {
            step.step_id
            for step in plan.steps
            if step.status == PlanStepStatus.SUCCESS
        }

        for step in plan.steps:
            if step.status in [
                PlanStepStatus.SUCCESS,
                PlanStepStatus.FAILED,
                PlanStepStatus.SKIPPED,
                PlanStepStatus.RUNNING,
            ]:
                continue

            if all(dep in success_ids for dep in step.dependencies):
                step.status = PlanStepStatus.READY
            else:
                step.status = PlanStepStatus.PENDING

    def next_ready_step(
        self,
        plan: DeepPlan,
    ) -> PlanStep | None:
        self.refresh_step_status(plan)

        for step in plan.steps:
            if step.status == PlanStepStatus.READY:
                return step

        return None

    def should_replan(
        self,
        plan: DeepPlan,
    ) -> bool:
        failed_steps = [
            step for step in plan.steps
            if step.status == PlanStepStatus.FAILED
        ]

        return len(failed_steps) > 0

    def replan_after_failure(
        self,
        plan: DeepPlan,
        failed_step: PlanStep,
    ) -> DeepPlan:
        """
        教学版动态 Replan。

        如果资料收集失败，就追加一个备用资料收集步骤。
        """

        if failed_step.step_type == PlanStepType.TOOL:
            new_step_id = f"step_backup_{uuid.uuid4().hex[:6]}"

            backup_step = PlanStep(
                step_id=new_step_id,
                title="使用备用方式补充资料",
                description="原工具失败后，使用备用搜索策略补充资料。",
                step_type=PlanStepType.TOOL,
                dependencies=[],
                tool_name="backup_search",
                tool_input={
                    "query": plan.user_goal,
                },
                output_file="/backup_research_notes.md",
                max_retries=1,
            )

            plan.steps.insert(
                0,
                backup_step,
            )

            failed_step.status = PlanStepStatus.SKIPPED
            failed_step.error_message = (
                failed_step.error_message or "已跳过失败步骤，改用备用步骤。"
            )

        self.refresh_step_status(plan)

        return plan

    def _classify_task(
        self,
        user_goal: str,
    ) -> PlanningTaskType:
        if any(word in user_goal for word in ["调研", "竞品", "研究"]):
            return PlanningTaskType.RESEARCH

        if any(word in user_goal for word in ["报告", "方案", "文档"]):
            return PlanningTaskType.REPORT

        if any(word in user_goal for word in ["代码", "仓库", "Bug", "bug"]):
            return PlanningTaskType.CODE_ANALYSIS

        if any(word in user_goal for word in ["数据", "指标", "报表"]):
            return PlanningTaskType.DATA_ANALYSIS

        return PlanningTaskType.GENERAL

    def _create_research_report_steps(
        self,
        user_goal: str,
    ) -> list[PlanStep]:
        return [
            PlanStep(
                step_id="step_001",
                title="明确任务目标",
                description="分析用户目标，确定输出格式和研究范围。",
                step_type=PlanStepType.THINK,
                output_file="/task_brief.md",
            ),
            PlanStep(
                step_id="step_002",
                title="收集资料",
                description="调用资料检索工具，收集和任务相关的信息。",
                step_type=PlanStepType.TOOL,
                dependencies=["step_001"],
                tool_name="search",
                tool_input={
                    "query": user_goal,
                },
                output_file="/research_notes.md",
                max_retries=2,
            ),
            PlanStep(
                step_id="step_003",
                title="分析资料",
                description="把资料交给分析子 Agent，提炼结构化结论。",
                step_type=PlanStepType.SUBAGENT,
                dependencies=["step_002"],
                subagent_name="analysis-agent",
                output_file="/analysis_notes.md",
            ),
            PlanStep(
                step_id="step_004",
                title="生成报告草稿",
                description="根据任务目标、研究资料和分析结论生成报告草稿。",
                step_type=PlanStepType.WRITE_FILE,
                dependencies=["step_003"],
                output_file="/draft_report.md",
            ),
            PlanStep(
                step_id="step_005",
                title="审查报告",
                description="检查报告是否有结构缺失、结论空泛、来源不足等问题。",
                step_type=PlanStepType.REVIEW,
                dependencies=["step_004"],
                subagent_name="reviewer-agent",
                output_file="/review_notes.md",
            ),
            PlanStep(
                step_id="step_006",
                title="输出最终报告",
                description="结合草稿和审查意见，输出最终报告。",
                step_type=PlanStepType.FINAL,
                dependencies=["step_005"],
                output_file="/final_report.md",
            ),
        ]

    def _create_code_analysis_steps(
        self,
        user_goal: str,
    ) -> list[PlanStep]:
        return [
            PlanStep(
                step_id="step_001",
                title="读取项目结构",
                description="分析代码仓库目录结构。",
                step_type=PlanStepType.TOOL,
                tool_name="inspect_project",
                tool_input={
                    "query": user_goal,
                },
                output_file="/project_structure.md",
            ),
            PlanStep(
                step_id="step_002",
                title="分析核心模块",
                description="根据目录结构分析核心模块和调用关系。",
                step_type=PlanStepType.SUBAGENT,
                dependencies=["step_001"],
                subagent_name="code-analysis-agent",
                output_file="/code_analysis.md",
            ),
            PlanStep(
                step_id="step_003",
                title="输出分析报告",
                description="输出代码仓库分析报告。",
                step_type=PlanStepType.FINAL,
                dependencies=["step_002"],
                output_file="/final_report.md",
            ),
        ]

    def _create_data_analysis_steps(
        self,
        user_goal: str,
    ) -> list[PlanStep]:
        return [
            PlanStep(
                step_id="step_001",
                title="明确分析指标",
                description="明确要分析的数据指标和口径。",
                step_type=PlanStepType.THINK,
                output_file="/metric_brief.md",
            ),
            PlanStep(
                step_id="step_002",
                title="分析数据",
                description="调用数据分析子 Agent 生成分析结论。",
                step_type=PlanStepType.SUBAGENT,
                dependencies=["step_001"],
                subagent_name="data-analysis-agent",
                output_file="/data_analysis.md",
            ),
            PlanStep(
                step_id="step_003",
                title="输出数据报告",
                description="输出数据分析报告。",
                step_type=PlanStepType.FINAL,
                dependencies=["step_002"],
                output_file="/final_report.md",
            ),
        ]

    def _create_general_steps(
        self,
        user_goal: str,
    ) -> list[PlanStep]:
        return [
            PlanStep(
                step_id="step_001",
                title="理解问题",
                description="理解用户目标。",
                step_type=PlanStepType.THINK,
                output_file="/task_brief.md",
            ),
            PlanStep(
                step_id="step_002",
                title="输出结果",
                description="输出最终回答。",
                step_type=PlanStepType.FINAL,
                dependencies=["step_001"],
                output_file="/final_answer.md",
            ),
        ]