from app.deepagents_subagent.agents import (
    SubAgentRegistry,
    build_default_subagent_specs,
)
from app.deepagents_subagent.router import SubAgentTaskRouter
from app.deepagents_subagent.schemas import (
    MainAgentRunResult,
    SubAgentResult,
    SubAgentStatus,
)
from app.deepagents_subagent.tools import (
    SubAgentToolExecutor,
    build_subagent_tools,
)
from app.deepagents_subagent.workspace import SubAgentWorkspace


class MainAgentOrchestrator:
    """
    教学版主 Agent。

    职责：
    1. 分析用户目标。
    2. 决定是否委派 Sub-Agent。
    3. 按顺序调用 Sub-Agent。
    4. 收集结果。
    5. 汇总最终回答。
    """

    def __init__(
        self,
        workspace: SubAgentWorkspace | None = None,
    ):
        self.workspace = workspace or SubAgentWorkspace()
        self.tool_executor = SubAgentToolExecutor(
            build_subagent_tools()
        )
        self.registry = SubAgentRegistry(
            specs=build_default_subagent_specs(),
            tool_executor=self.tool_executor,
        )
        self.router = SubAgentTaskRouter()

    def list_subagents(self):
        return self.registry.list_specs()

    def run(
        self,
        user_goal: str,
    ) -> MainAgentRunResult:
        trace: list[str] = []

        trace.append(
            f"MainAgent 收到任务：{user_goal}"
        )

        decisions = self.router.decide(user_goal)

        trace.append(
            f"生成委派决策数量：{len(decisions)}"
        )

        results: list[SubAgentResult] = []
        accumulated_context = ""

        for decision in decisions:
            if not decision.should_delegate:
                trace.append(
                    f"不委派：{decision.reason}"
                )
                continue

            trace.append(
                f"委派给 {decision.agent_name}，原因：{decision.reason}"
            )

            expected_output = self._build_expected_output(
                decision.agent_name or ""
            )

            result = self.registry.run(
                agent_name=decision.agent_name or "",
                instruction=decision.task_instruction,
                input_context=accumulated_context,
                expected_output=expected_output,
                write_file=self.workspace.write_file,
            )

            results.append(result)

            trace.append(
                f"{result.agent_name} 返回状态：{result.status.value}"
            )

            if result.status == SubAgentStatus.SUCCESS:
                accumulated_context += (
                    f"\n\n## {result.agent_name} 输出\n\n"
                    f"{result.output}"
                )
            else:
                accumulated_context += (
                    f"\n\n## {result.agent_name} 失败\n\n"
                    f"{result.error_message}"
                )

        final_answer = self._synthesize_final_answer(
            user_goal=user_goal,
            results=results,
            accumulated_context=accumulated_context,
        )

        self.workspace.write_file(
            "/final_answer.md",
            final_answer,
        )

        trace.append(
            "MainAgent 已生成最终回答。"
        )

        return MainAgentRunResult(
            user_goal=user_goal,
            delegation_results=results,
            final_answer=final_answer,
            files=self.workspace.list_files(),
            trace=trace,
        )

    def run_parallel_simulation(
        self,
        user_goal: str,
    ) -> MainAgentRunResult:
        """
        教学版并行模拟。

        注意：
        这里为了简单没有真正 asyncio 并发，
        只是展示哪些任务可以独立委派。
        """
        trace: list[str] = [
            f"MainAgent 收到并行任务：{user_goal}"
        ]

        parallel_tasks = [
            (
                "research-agent",
                f"调研 Dify 平台：{user_goal}",
            ),
            (
                "research-agent",
                f"调研 Coze 平台：{user_goal}",
            ),
            (
                "research-agent",
                f"调研 LangGraph 平台：{user_goal}",
            ),
        ]

        results: list[SubAgentResult] = []
        accumulated_context = ""

        for agent_name, instruction in parallel_tasks:
            trace.append(
                f"模拟并行委派给 {agent_name}：{instruction}"
            )

            result = self.registry.run(
                agent_name=agent_name,
                instruction=instruction,
                input_context="",
                expected_output="输出单个平台研究笔记。",
                write_file=self.workspace.write_file,
            )

            results.append(result)
            accumulated_context += (
                f"\n\n## {instruction}\n\n{result.output}"
            )

        analysis_result = self.registry.run(
            agent_name="analysis-agent",
            instruction="综合多个平台研究结果，输出对比分析。",
            input_context=accumulated_context,
            expected_output="输出综合分析。",
            write_file=self.workspace.write_file,
        )
        results.append(analysis_result)

        final_answer = self._synthesize_final_answer(
            user_goal=user_goal,
            results=results,
            accumulated_context=accumulated_context + analysis_result.output,
        )

        self.workspace.write_file(
            "/parallel_final_answer.md",
            final_answer,
        )

        trace.append(
            "并行模拟流程完成。"
        )

        return MainAgentRunResult(
            user_goal=user_goal,
            delegation_results=results,
            final_answer=final_answer,
            files=self.workspace.list_files(),
            trace=trace,
        )

    def _build_expected_output(
        self,
        agent_name: str,
    ) -> str:
        if agent_name == "research-agent":
            return "输出研究笔记，包含事实、来源、关键发现。"

        if agent_name == "analysis-agent":
            return "输出结构化分析，包含结论、依据、风险。"

        if agent_name == "writer-agent":
            return "输出 Markdown 报告草稿。"

        if agent_name == "reviewer-agent":
            return "输出审查意见和修改建议。"

        if agent_name == "code-agent":
            return "输出代码分析报告。"

        if agent_name == "data-agent":
            return "输出数据分析结论。"

        return "输出子任务结果。"

    def _synthesize_final_answer(
        self,
        user_goal: str,
        results: list[SubAgentResult],
        accumulated_context: str,
    ) -> str:
        success_results = [
            item for item in results
            if item.status == SubAgentStatus.SUCCESS
        ]

        failed_results = [
            item for item in results
            if item.status == SubAgentStatus.FAILED
        ]

        summaries = "\n".join(
            f"- {item.agent_name}：{item.summary}"
            for item in success_results
        )

        warnings = []

        for item in results:
            warnings.extend(item.warnings)

        warning_text = "\n".join(
            f"- {item}"
            for item in warnings
        ) or "暂无明显风险。"

        failed_text = "\n".join(
            f"- {item.agent_name}：{item.error_message}"
            for item in failed_results
        ) or "无失败子任务。"

        return f"""
# Sub-Agent 协作结果

## 一、用户目标

{user_goal}

## 二、子任务完成情况

{summaries}

## 三、失败子任务

{failed_text}

## 四、综合结论

本次任务通过 Main Agent 委派多个 Sub-Agent 完成。Research Agent 负责资料收集，Analysis Agent 负责分析，Writer Agent 负责生成草稿，Reviewer Agent 负责审查。主 Agent 不直接处理所有细节，而是负责规划、委派、收集结果和最终整合。

## 五、风险和提醒

{warning_text}

## 六、完整上下文摘要

{accumulated_context[:3000]}
""".strip()