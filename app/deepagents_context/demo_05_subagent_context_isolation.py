from dataclasses import asdict

from app.deepagents_context.context_manager import DeepAgentContextManager
from app.deepagents_context.workspace import ContextWorkspace


def main():
    workspace = ContextWorkspace(
        "data/deepagents_context_workspace_demo_05"
    )
    workspace.clear()

    manager = DeepAgentContextManager(
        workspace=workspace
    )

    raw_output = "\n".join([
        f"Research Agent 详细资料第 {index} 条：这里是大量原始搜索结果和分析过程。"
        for index in range(1, 80)
    ])

    result = manager.create_subagent_result(
        agent_name="research-agent",
        task="调研 DeepAgents Context 管理",
        raw_output=raw_output,
    )

    print("SubAgentContextResult:")
    print(asdict(result))

    print("=" * 80)
    print("workspace files:")
    print(workspace.list_files())

    print("=" * 80)
    print("main agent only receives summary:")
    print(result.summary)


if __name__ == "__main__":
    main()