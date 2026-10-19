from dataclasses import asdict

from app.deepagents_context.context_manager import DeepAgentContextManager
from app.deepagents_context.memory import memory_store
from app.deepagents_context.schemas import (
    ContextBudget,
    ContextRunResult,
)
from app.deepagents_context.workspace import ContextWorkspace


class DeepAgentsContextService:
    def __init__(self):
        self.workspace = ContextWorkspace()
        self.manager = DeepAgentContextManager(
            workspace=self.workspace
        )

    def setup_demo_memory(
        self,
        user_id: str,
    ) -> None:
        memory_store.add_preference(
            user_id,
            "用户偏好：输出课程章节时要口语化，方便复制，不要 AI 味。",
        )
        memory_store.add_preference(
            user_id,
            "用户偏好：代码要能直接运行，最好提供 scripts 测试入口。",
        )
        memory_store.add_project_term(
            user_id,
            "项目术语：DeepAgents 阶段包含 Planning、Sub-Agent、Context 管理和 Deep Research Agent。",
        )
        memory_store.add_project_term(
            user_id,
            "项目术语：企业知识库项目包含 RAG、Chunk、Embedding、Retrieval、Evaluation。",
        )

    def run_demo(
        self,
        user_goal: str,
        user_id: str = "anonymous",
        max_tokens: int = 3000,
    ) -> dict:
        self.setup_demo_memory(user_id)

        long_tool_result = self._mock_long_tool_result()
        long_subagent_output = self._mock_long_subagent_output()

        subagent_result = self.manager.create_subagent_result(
            agent_name="research-agent",
            task="调研 DeepAgents Context 管理",
            raw_output=long_subagent_output,
        )

        context_pack = self.manager.build_context_pack(
            user_goal=user_goal,
            user_id=user_id,
            system_context=(
                "你是企业级 DeepAgent。"
                "你需要根据当前上下文完成复杂任务，并严格区分资料、记忆和推断。"
            ),
            messages=[
                "用户上一轮要求：继续生成 DeepAgents 相关章节。",
                "用户强调：生成标准按照之前完整章节模式。",
            ],
            plan_summary=(
                "当前计划：先解释 Context 管理，再实现 ContextManager，"
                "最后输出代码、接口、面试话术和课后任务。"
            ),
            tool_results=[
                long_tool_result,
                "短工具结果：DeepAgents 使用 workspace 保存中间文件。",
            ],
            subagent_results=[
                subagent_result,
            ],
            rag_chunks=[
                "RAG 片段：DeepAgent 可以调用企业知识库检索项目资料。",
                "RAG 片段：Context Pack 应该只包含当前步骤需要的资料。",
            ],
            budget=ContextBudget(
                max_tokens=max_tokens,
                reserved_for_system=400,
                reserved_for_user_goal=300,
                reserved_for_answer=700,
            ),
        )

        result = ContextRunResult(
            user_goal=user_goal,
            context_pack=context_pack,
            prompt_preview=context_pack.to_prompt(),
            files=self.workspace.list_files(),
            trace=[
                "已创建 demo memory",
                "已模拟长工具结果",
                "已将长 Sub-Agent 输出写入 workspace",
                "已构建 ContextPack",
            ],
        )

        return asdict(result)

    def list_files(self) -> list[str]:
        return self.workspace.list_files()

    def read_file(
        self,
        file_path: str,
    ) -> str:
        return self.workspace.read_file(file_path)

    def clear_workspace(self) -> None:
        self.workspace.clear()

    def _mock_long_tool_result(self) -> str:
        paragraphs = []

        for index in range(1, 30):
            paragraphs.append(
                f"第 {index} 条工具结果：DeepAgents Context 管理需要处理 "
                "messages、state、workspace、memory、store、RAG chunks、"
                "subagent results、tool results、trace logs 等内容。"
                "如果全部进入 active context，会导致上下文爆炸。"
            )

        return "\n".join(paragraphs)

    def _mock_long_subagent_output(self) -> str:
        return """
# Research Agent Raw Output

## 资料一

DeepAgents Context 管理强调不能把所有信息都塞入 messages。

## 资料二

长工具结果应该写入 workspace，并在 active context 中保留摘要和文件指针。

## 资料三

Sub-Agent 可以隔离复杂任务上下文，主 Agent 只接收 summary、warnings 和 output_file。

## 资料四

Memory 应该保存长期稳定偏好，而不是保存一次性任务过程。

## 资料五

Context Pack 要根据当前步骤动态构建，而不是每次都使用全量上下文。

## 结论

DeepAgents Context 管理的核心是 Offload、Reduce、Isolate。
""" * 3


deepagents_context_service = DeepAgentsContextService()