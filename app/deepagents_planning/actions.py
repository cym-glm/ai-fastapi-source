from app.deepagents_planning.schemas import (
    PlanObservation,
    PlanStep,
    PlanStepType,
)


class PlanningActionExecutor:
    """
    教学版动作执行器。

    根据 step_type 执行不同动作。
    """

    def execute(
        self,
        step: PlanStep,
        user_goal: str,
        read_file,
        write_file,
    ) -> PlanObservation:
        try:
            if step.step_type == PlanStepType.THINK:
                return self._execute_think(
                    step,
                    user_goal,
                    write_file,
                )

            if step.step_type == PlanStepType.TOOL:
                return self._execute_tool(
                    step,
                    write_file,
                )

            if step.step_type == PlanStepType.SUBAGENT:
                return self._execute_subagent(
                    step,
                    read_file,
                    write_file,
                )

            if step.step_type == PlanStepType.WRITE_FILE:
                return self._execute_write_file(
                    step,
                    user_goal,
                    read_file,
                    write_file,
                )

            if step.step_type == PlanStepType.REVIEW:
                return self._execute_review(
                    step,
                    read_file,
                    write_file,
                )

            if step.step_type == PlanStepType.FINAL:
                return self._execute_final(
                    step,
                    user_goal,
                    read_file,
                    write_file,
                )

            return PlanObservation(
                step_id=step.step_id,
                success=False,
                output="",
                error_message=f"不支持的 step_type：{step.step_type}",
            )

        except Exception as exc:
            return PlanObservation(
                step_id=step.step_id,
                success=False,
                output="",
                error_message=str(exc),
            )

    def _execute_think(
        self,
        step: PlanStep,
        user_goal: str,
        write_file,
    ) -> PlanObservation:
        content = f"""
            # 任务理解

            用户目标：
            {user_goal}

            当前步骤：
            {step.title}

            执行说明：
            本任务需要先拆解目标，再收集资料、分析资料、生成结果并进行审查。
""".strip()

        if step.output_file:
            write_file(
                step.output_file,
                content,
            )

        return PlanObservation(
            step_id=step.step_id,
            success=True,
            output=content,
        )

    def _execute_tool(
        self,
        step: PlanStep,
        write_file,
    ) -> PlanObservation:
        query = step.tool_input.get(
            "query",
            "",
        )

        # 教学用：模拟失败。
        if "失败测试" in query and step.retry_count == 0:
            return PlanObservation(
                step_id=step.step_id,
                success=False,
                output="",
                error_message="模拟搜索工具第一次失败。",
            )

        if step.tool_name == "backup_search":
            content = (
                "备用搜索结果：补充找到 DeepAgents Planning 的关键资料："
                "任务拆解、Todo、Plan-Act-Observe、动态计划更新、失败重试。"
            )
        else:
            content = (
                f"资料检索结果：围绕「{query}」找到以下信息：\n"
                "1. DeepAgents 适合复杂长任务。\n"
                "2. Planning 用于任务拆解和步骤管理。\n"
                "3. Todo List 用于记录任务状态。\n"
                "4. Workspace 用于保存中间结果。\n"
                "5. SubAgent 可以处理专业子任务。\n"
            )

        if step.output_file:
            write_file(
                step.output_file,
                content,
            )

        return PlanObservation(
            step_id=step.step_id,
            success=True,
            output=content,
        )

    def _execute_subagent(
        self,
        step: PlanStep,
        read_file,
        write_file,
    ) -> PlanObservation:
        research = self._safe_read(
            read_file,
            "/research_notes.md",
        ) + self._safe_read(
            read_file,
            "/backup_research_notes.md",
        )

        if "analysis" in (step.subagent_name or ""):
            content = (
                "AnalysisSubAgent 结论：\n"
                "1. Planning 可以让复杂任务更稳定。\n"
                "2. Todo 状态让任务执行过程可追踪。\n"
                "3. 失败重试和 Replan 可以提升复杂任务鲁棒性。\n"
                "4. Workspace 能减少上下文堆积。\n\n"
                f"参考资料：\n{research}"
            )
        elif "code" in (step.subagent_name or ""):
            content = "CodeAnalysisSubAgent 结论：项目结构需要按 API、Service、Repository、Model 分层分析。"
        elif "data" in (step.subagent_name or ""):
            content = "DataAnalysisSubAgent 结论：需要明确指标口径、数据来源和异常值处理。"
        else:
            content = "SubAgent 子任务已完成。"

        if step.output_file:
            write_file(
                step.output_file,
                content,
            )

        return PlanObservation(
            step_id=step.step_id,
            success=True,
            output=content,
        )

    def _execute_write_file(
        self,
        step: PlanStep,
        user_goal: str,
        read_file,
        write_file,
    ) -> PlanObservation:
        research = self._safe_read(
            read_file,
            "/research_notes.md",
        )

        analysis = self._safe_read(
            read_file,
            "/analysis_notes.md",
        )

        content = f"""
# DeepAgents Planning 报告草稿

## 一、任务目标

{user_goal}

## 二、资料整理

{research}

## 三、分析结论

{analysis}

## 四、初步结论

DeepAgents Planning 的核心不是简单生成步骤列表，而是让 Agent 能按照计划执行、记录观察结果、更新状态，并在失败时重试或重新规划。
""".strip()

        if step.output_file:
            write_file(
                step.output_file,
                content,
            )

        return PlanObservation(
            step_id=step.step_id,
            success=True,
            output=content,
        )

    def _execute_review(
        self,
        step: PlanStep,
        read_file,
        write_file,
    ) -> PlanObservation:
        draft = self._safe_read(
            read_file,
            "/draft_report.md",
        )

        checks = []

        if "任务目标" in draft:
            checks.append("已包含任务目标。")
        else:
            checks.append("缺少任务目标。")

        if "资料整理" in draft:
            checks.append("已包含资料整理。")
        else:
            checks.append("缺少资料整理。")

        if "分析结论" in draft:
            checks.append("已包含分析结论。")
        else:
            checks.append("缺少分析结论。")

        if "失败" in draft or "重试" in draft or "重新规划" in draft:
            checks.append("已提到失败处理或动态规划。")
        else:
            checks.append("建议补充失败处理和动态规划说明。")

        content = "\n".join(
            f"- {item}"
            for item in checks
        )

        if step.output_file:
            write_file(
                step.output_file,
                content,
            )

        return PlanObservation(
            step_id=step.step_id,
            success=True,
            output=content,
        )

    def _execute_final(
        self,
        step: PlanStep,
        user_goal: str,
        read_file,
        write_file,
    ) -> PlanObservation:
        draft = self._safe_read(
            read_file,
            "/draft_report.md",
        )

        review = self._safe_read(
            read_file,
            "/review_notes.md",
        )

        if not draft:
            draft = f"# 最终回答\n\n任务：{user_goal}"

        content = f"""
{draft}

## 五、Review 结果

{review}

## 六、最终总结

本次任务通过 Planning 拆解为多个可执行步骤，每一步都有状态、产物和执行结果。相比普通 Agent，Planning Agent 更适合复杂长任务，因为它可以追踪进度、沉淀中间文件、处理失败重试，并在必要时动态更新计划。
""".strip()

        if step.output_file:
            write_file(
                step.output_file,
                content,
            )

        return PlanObservation(
            step_id=step.step_id,
            success=True,
            output=content,
        )

    def _safe_read(
        self,
        read_file,
        file_path: str,
    ) -> str:
        try:
            return read_file(file_path)
        except FileNotFoundError:
            return ""