from app.deepagents_subagent.schemas import (
    DelegationDecision,
)


class SubAgentTaskRouter:
    """
    主 Agent 的任务委派决策器。

    教学版：基于规则决定委派给哪个 Sub-Agent。
    生产环境可以替换成 LLM Router + Structured Output。
    """

    def decide(
        self,
        user_goal: str,
    ) -> list[DelegationDecision]:
        decisions: list[DelegationDecision] = []

        if any(word in user_goal for word in ["调研", "竞品", "研究"]):
            decisions.append(
                DelegationDecision(
                    should_delegate=True,
                    agent_name="research-agent",
                    reason="任务需要资料收集和竞品调研。",
                    task_instruction=(
                        f"围绕用户目标进行资料收集和研究笔记整理：{user_goal}"
                    ),
                )
            )

            decisions.append(
                DelegationDecision(
                    should_delegate=True,
                    agent_name="analysis-agent",
                    reason="任务需要结构化分析和趋势判断。",
                    task_instruction=(
                        f"基于研究资料分析趋势、风险和落地建议：{user_goal}"
                    ),
                )
            )

            decisions.append(
                DelegationDecision(
                    should_delegate=True,
                    agent_name="writer-agent",
                    reason="任务需要输出结构化报告。",
                    task_instruction=(
                        f"根据资料和分析结论写一份结构化报告：{user_goal}"
                    ),
                )
            )

            decisions.append(
                DelegationDecision(
                    should_delegate=True,
                    agent_name="reviewer-agent",
                    reason="最终报告需要审查。",
                    task_instruction=(
                        "检查报告结构、事实依据、风险分析和遗漏点。"
                    ),
                )
            )

            return decisions

        if any(word in user_goal for word in ["代码", "仓库", "Bug", "bug"]):
            return [
                DelegationDecision(
                    should_delegate=True,
                    agent_name="code-agent",
                    reason="任务需要代码仓库分析。",
                    task_instruction=f"分析代码仓库并输出结构化技术报告：{user_goal}",
                )
            ]

        if any(word in user_goal for word in ["数据", "指标", "报表"]):
            return [
                DelegationDecision(
                    should_delegate=True,
                    agent_name="data-agent",
                    reason="任务需要数据分析。",
                    task_instruction=f"分析数据指标并输出业务结论：{user_goal}",
                )
            ]

        return [
            DelegationDecision(
                should_delegate=False,
                agent_name=None,
                reason="任务较简单，不需要委派 Sub-Agent。",
            )
        ]