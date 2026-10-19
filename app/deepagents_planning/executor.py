from app.deepagents_planning.actions import PlanningActionExecutor
from app.deepagents_planning.planner import RuleBasedDeepPlanner
from app.deepagents_planning.schemas import (
    DeepPlan,
    PlanExecutionTrace,
    PlanRunResult,
    PlanStep,
    PlanStepStatus,
)
from app.deepagents_planning.workspace import PlanningWorkspace


class DeepPlanningExecutor:
    def __init__(
        self,
        workspace: PlanningWorkspace | None = None,
    ):
        self.planner = RuleBasedDeepPlanner()
        self.action_executor = PlanningActionExecutor()
        self.workspace = workspace or PlanningWorkspace()

    def run_plan(
        self,
        plan: DeepPlan,
        allow_replan: bool = True,
    ) -> PlanRunResult:
        trace: list[PlanExecutionTrace] = []

        trace.append(
            PlanExecutionTrace(
                event="plan_started",
                message=f"开始执行计划：{plan.plan_id}",
            )
        )

        self._write_plan_file(plan)

        while True:
            step = self.planner.next_ready_step(plan)

            if not step:
                break

            trace.append(
                PlanExecutionTrace(
                    event="step_started",
                    step_id=step.step_id,
                    message=f"开始执行步骤：{step.title}",
                )
            )

            step.status = PlanStepStatus.RUNNING

            observation = self.action_executor.execute(
                step=step,
                user_goal=plan.user_goal,
                read_file=self.workspace.read_file,
                write_file=self.workspace.write_file,
            )

            if observation.success:
                step.status = PlanStepStatus.SUCCESS
                step.result = observation.output
                step.error_message = None

                trace.append(
                    PlanExecutionTrace(
                        event="step_success",
                        step_id=step.step_id,
                        message=f"步骤成功：{step.title}",
                    )
                )

            else:
                step.retry_count += 1
                step.error_message = observation.error_message

                trace.append(
                    PlanExecutionTrace(
                        event="step_failed",
                        step_id=step.step_id,
                        message=observation.error_message or "步骤失败",
                    )
                )

                if step.retry_count <= step.max_retries:
                    step.status = PlanStepStatus.READY

                    trace.append(
                        PlanExecutionTrace(
                            event="step_retry",
                            step_id=step.step_id,
                            message=(
                                f"准备重试：{step.retry_count}/"
                                f"{step.max_retries}"
                            ),
                        )
                    )

                else:
                    step.status = PlanStepStatus.FAILED

                    if allow_replan:
                        trace.append(
                            PlanExecutionTrace(
                                event="replan_started",
                                step_id=step.step_id,
                                message="步骤失败次数超过上限，开始动态 Replan。",
                            )
                        )

                        self.planner.replan_after_failure(
                            plan=plan,
                            failed_step=step,
                        )

                        trace.append(
                            PlanExecutionTrace(
                                event="replan_finished",
                                step_id=step.step_id,
                                message="动态 Replan 完成。",
                            )
                        )

            self.planner.refresh_step_status(plan)
            self._write_plan_file(plan)

        final_answer = self._build_final_answer(plan)

        trace.append(
            PlanExecutionTrace(
                event="plan_finished",
                message=f"计划执行完成：{plan.plan_id}",
            )
        )

        return PlanRunResult(
            plan_id=plan.plan_id,
            user_goal=plan.user_goal,
            final_answer=final_answer,
            steps=plan.steps,
            files=self.workspace.list_files(),
            trace=trace,
        )

    def run_goal(
        self,
        user_goal: str,
        allow_replan: bool = True,
    ) -> PlanRunResult:
        plan = self.planner.create_plan(user_goal)

        return self.run_plan(
            plan=plan,
            allow_replan=allow_replan,
        )

    def _write_plan_file(
        self,
        plan: DeepPlan,
    ) -> None:
        content = self._format_plan(plan)

        self.workspace.write_file(
            "/plan.md",
            content,
        )

    def _format_plan(
        self,
        plan: DeepPlan,
    ) -> str:
        lines = [
            "# DeepAgent Plan",
            "",
            f"Plan ID：{plan.plan_id}",
            f"Task Type：{plan.task_type.value}",
            f"User Goal：{plan.user_goal}",
            "",
            "## Steps",
            "",
        ]

        for step in plan.steps:
            lines.append(
                f"### {step.step_id}｜{step.title}"
            )
            lines.append(
                f"- status：{step.status.value}"
            )
            lines.append(
                f"- type：{step.step_type.value}"
            )
            lines.append(
                f"- dependencies：{step.dependencies}"
            )
            lines.append(
                f"- output_file：{step.output_file}"
            )
            lines.append(
                f"- retry：{step.retry_count}/{step.max_retries}"
            )

            if step.error_message:
                lines.append(
                    f"- error：{step.error_message}"
                )

            if step.result:
                lines.append(
                    f"- result：{step.result[:200]}"
                )

            lines.append("")

        return "\n".join(lines)

    def _build_final_answer(
        self,
        plan: DeepPlan,
    ) -> str:
        final_files = [
            "/final_report.md",
            "/final_answer.md",
        ]

        for file_path in final_files:
            try:
                return self.workspace.read_file(file_path)
            except FileNotFoundError:
                continue

        success_steps = [
            step for step in plan.steps
            if step.status == PlanStepStatus.SUCCESS
        ]

        failed_steps = [
            step for step in plan.steps
            if step.status == PlanStepStatus.FAILED
        ]

        return (
            f"计划 {plan.plan_id} 执行完成。"
            f"成功步骤：{len(success_steps)}，失败步骤：{len(failed_steps)}。"
        )