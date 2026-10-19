from app.deepagents_core.schemas import (
    DeepSubAgentResult,
    DeepSubAgentSpec,
)


class TeachingSubAgentRunner:
    def __init__(
        self,
        subagents: list[DeepSubAgentSpec],
    ):
        self.subagents = {
            subagent.name: subagent
            for subagent in subagents
        }

    def run(
        self,
        name: str,
        task: str,
    ) -> DeepSubAgentResult:
        subagent = self.subagents.get(name)

        if not subagent:
            return DeepSubAgentResult(
                name=name,
                task=task,
                result="",
                success=False,
            )

        if "research" in name:
            result = (
                f"{subagent.description}\n"
                f"任务：{task}\n"
                "结果：已整理 DeepAgents、RAG、LangGraph、Multi-Agent 的关系。"
            )
        elif "writer" in name:
            result = (
                f"{subagent.description}\n"
                f"任务：{task}\n"
                "结果：已生成结构化报告草稿。"
            )
        elif "reviewer" in name:
            result = (
                f"{subagent.description}\n"
                f"任务：{task}\n"
                "结果：已检查报告结构，建议补充风险和落地建议。"
            )
        else:
            result = (
                f"{subagent.description}\n"
                f"任务：{task}\n"
                "结果：子任务已完成。"
            )

        return DeepSubAgentResult(
            name=name,
            task=task,
            result=result,
        )


def build_default_subagents() -> list[DeepSubAgentSpec]:
    return [
        DeepSubAgentSpec(
            name="research-agent",
            description="负责资料收集和研究笔记整理。",
            system_prompt=(
                "你是 Research SubAgent，只负责收集资料和整理事实，"
                "不要输出最终报告。"
            ),
        ),
        DeepSubAgentSpec(
            name="writer-agent",
            description="负责根据资料生成报告草稿。",
            system_prompt=(
                "你是 Writer SubAgent，只负责写结构化报告草稿。"
            ),
        ),
        DeepSubAgentSpec(
            name="reviewer-agent",
            description="负责检查报告质量和遗漏点。",
            system_prompt=(
                "你是 Reviewer SubAgent，只负责审查和提出修改建议。"
            ),
        ),
    ]