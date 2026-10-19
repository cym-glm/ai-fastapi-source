import uuid

from app.deepagents_core.backend import (
    LocalFilesystemDeepAgentBackend,
)
from app.deepagents_core.graph import create_teaching_deep_agent
from app.deepagents_core.subagents import build_default_subagents
from app.deepagents_core.tools import build_default_tools


DEFAULT_DEEP_AGENT_SYSTEM_PROMPT = """
你是企业级 DeepAgent。

工作方式：
1. 遇到复杂任务，先生成 Todo List。
2. 按步骤完成任务，不要跳过分析过程。
3. 需要资料时，先调用工具检索。
4. 中间资料写入 workspace 文件。
5. 可以委派 subagent 完成资料整理、写作和审查。
6. 最终输出结构化结果。
7. 资料不足时要明确说明。
"""


class DeepAgentCoreService:
    def __init__(self):
        self.backend = LocalFilesystemDeepAgentBackend(
            root_dir="data/deepagents_core_workspace"
        )

        self.agent = create_teaching_deep_agent(
            model="teaching-deep-agent-model",
            tools=build_default_tools(),
            system_prompt=DEFAULT_DEEP_AGENT_SYSTEM_PROMPT,
            name="enterprise-deep-agent",
            subagents=build_default_subagents(),
            backend=self.backend,
            debug=True,
        )

    def run_task(
        self,
        user_request: str,
        tenant_id: str = "tenant_001",
        user_id: str = "anonymous",
        thread_id: str | None = None,
    ) -> dict:
        if not thread_id:
            thread_id = f"deep_thread_{uuid.uuid4().hex[:12]}"

        task_id = f"deep_task_{uuid.uuid4().hex[:12]}"

        return self.agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_request,
                    }
                ]
            },
            config={
                "configurable": {
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "thread_id": thread_id,
                    "task_id": task_id,
                }
            },
        )

    def list_workspace_files(
        self,
        thread_id: str,
    ) -> list[str]:
        return self.backend.list_files(thread_id)

    def read_workspace_file(
        self,
        thread_id: str,
        file_path: str,
    ) -> str:
        return self.backend.read_file(
            thread_id=thread_id,
            path=file_path,
        )


deep_agent_core_service = DeepAgentCoreService()