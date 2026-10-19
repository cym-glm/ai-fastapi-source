import uuid

from app.deepagents_context.compressor import SimpleContextCompressor
from app.deepagents_context.memory import memory_store
from app.deepagents_context.schemas import (
    ContextBudget,
    ContextItem,
    ContextPack,
    ContextPriority,
    ContextSource,
    SubAgentContextResult,
)
from app.deepagents_context.selector import ContextSelector
from app.deepagents_context.workspace import ContextWorkspace


class DeepAgentContextManager:
    def __init__(
        self,
        workspace: ContextWorkspace | None = None,
    ):
        self.workspace = workspace or ContextWorkspace()
        self.selector = ContextSelector()
        self.compressor = SimpleContextCompressor()

    def build_context_pack(
        self,
        user_goal: str,
        user_id: str = "anonymous",
        system_context: str | None = None,
        messages: list[str] | None = None,
        plan_summary: str | None = None,
        tool_results: list[str] | None = None,
        subagent_results: list[SubAgentContextResult] | None = None,
        rag_chunks: list[str] | None = None,
        budget: ContextBudget | None = None,
    ) -> ContextPack:
        budget = budget or ContextBudget()

        system_context = system_context or (
            "你是企业级 DeepAgent。"
            "你需要基于当前步骤需要的信息完成任务。"
            "不要编造，不要把资料不足的内容说成确定事实。"
        )

        items: list[ContextItem] = []

        items.append(
            ContextItem(
                item_id="user_goal",
                source=ContextSource.USER,
                priority=ContextPriority.CRITICAL,
                title="用户目标",
                content=user_goal,
            )
        )

        if plan_summary:
            items.append(
                ContextItem(
                    item_id="plan_summary",
                    source=ContextSource.PLAN,
                    priority=ContextPriority.CRITICAL,
                    title="当前计划",
                    content=plan_summary,
                )
            )

        for index, message in enumerate(messages or []):
            items.append(
                ContextItem(
                    item_id=f"message_{index}",
                    source=ContextSource.MESSAGE,
                    priority=ContextPriority.MEDIUM,
                    title=f"最近对话 {index + 1}",
                    content=message,
                )
            )

        for index, memory in enumerate(
            memory_store.select_relevant_memories(
                user_id=user_id,
                query=user_goal,
            )
        ):
            items.append(
                ContextItem(
                    item_id=f"memory_{index}",
                    source=ContextSource.MEMORY,
                    priority=ContextPriority.HIGH,
                    title=f"长期记忆 {index + 1}",
                    content=memory,
                )
            )

        for index, chunk in enumerate(rag_chunks or []):
            items.append(
                ContextItem(
                    item_id=f"rag_{index}",
                    source=ContextSource.RAG,
                    priority=ContextPriority.HIGH,
                    title=f"RAG 片段 {index + 1}",
                    content=chunk,
                )
            )

        for index, result in enumerate(tool_results or []):
            item = self._build_tool_result_item(
                index=index,
                content=result,
            )
            items.append(item)

        for index, result in enumerate(subagent_results or []):
            items.append(
                ContextItem(
                    item_id=f"subagent_{index}",
                    source=ContextSource.SUBAGENT,
                    priority=ContextPriority.HIGH,
                    title=f"{result.agent_name} 子任务结果",
                    content=result.summary,
                    file_path=result.output_file,
                    metadata={
                        "agent_name": result.agent_name,
                        "task": result.task,
                        "warnings": result.warnings,
                    },
                )
            )

        active, offloaded, dropped, warnings = self.selector.select(
            items=items,
            budget=budget,
        )

        total_tokens = sum(
            self.compressor.estimate_tokens(
                item.summary or item.content
            )
            for item in active
        )

        return ContextPack(
            system_context=system_context,
            user_goal=user_goal,
            active_items=active,
            offloaded_items=offloaded,
            dropped_items=dropped,
            total_estimated_tokens=total_tokens,
            warnings=warnings,
        )

    def offload_to_file(
        self,
        title: str,
        content: str,
        directory: str = "/offloaded",
    ) -> ContextItem:
        file_name = f"{uuid.uuid4().hex[:10]}.md"
        file_path = f"{directory}/{file_name}"

        self.workspace.write_file(
            file_path,
            content,
        )

        summary = self.compressor.summarize(
            content,
            max_chars=500,
        )

        return ContextItem(
            item_id=f"offloaded_{uuid.uuid4().hex[:8]}",
            source=ContextSource.FILE,
            priority=ContextPriority.MEDIUM,
            title=title,
            content=content,
            summary=summary,
            file_path=file_path,
        )

    def create_subagent_result(
        self,
        agent_name: str,
        task: str,
        raw_output: str,
    ) -> SubAgentContextResult:
        file_path = f"/subagents/{agent_name}_{uuid.uuid4().hex[:8]}.md"

        self.workspace.write_file(
            file_path,
            raw_output,
        )

        summary = self.compressor.summarize(
            raw_output,
            max_chars=600,
        )

        warnings = []

        if len(raw_output) > 3000:
            warnings.append(
                "子 Agent 输出较长，主 Agent 只接收摘要和文件指针。"
            )

        return SubAgentContextResult(
            agent_name=agent_name,
            task=task,
            summary=summary,
            output_file=file_path,
            warnings=warnings,
        )

    def _build_tool_result_item(
        self,
        index: int,
        content: str,
    ) -> ContextItem:
        estimated = self.compressor.estimate_tokens(content)

        if estimated > 600:
            file_path = f"/tool_results/tool_result_{index + 1}.md"
            self.workspace.write_file(
                file_path,
                content,
            )

            summary = self.compressor.summarize(
                content,
                max_chars=500,
            )

            return ContextItem(
                item_id=f"tool_result_{index}",
                source=ContextSource.TOOL_RESULT,
                priority=ContextPriority.MEDIUM,
                title=f"工具结果 {index + 1}",
                content=content,
                summary=summary,
                file_path=file_path,
            )

        return ContextItem(
            item_id=f"tool_result_{index}",
            source=ContextSource.TOOL_RESULT,
            priority=ContextPriority.MEDIUM,
            title=f"工具结果 {index + 1}",
            content=content,
        )