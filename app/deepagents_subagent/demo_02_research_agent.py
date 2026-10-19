from dataclasses import asdict

from app.deepagents_subagent.agents import (
    SubAgentRegistry,
    build_default_subagent_specs,
)
from app.deepagents_subagent.tools import (
    SubAgentToolExecutor,
    build_subagent_tools,
)
from app.deepagents_subagent.workspace import SubAgentWorkspace


def main():
    workspace = SubAgentWorkspace(
        "data/deepagents_subagent_workspace_demo_02"
    )
    workspace.clear()

    tool_executor = SubAgentToolExecutor(
        build_subagent_tools()
    )

    registry = SubAgentRegistry(
        specs=build_default_subagent_specs(),
        tool_executor=tool_executor,
    )

    result = registry.run(
        agent_name="research-agent",
        instruction="调研 AI Agent 平台竞品，包括 Dify、Coze、LangGraph。",
        input_context="",
        expected_output="输出研究笔记。",
        write_file=workspace.write_file,
    )

    print(asdict(result))

    print("=" * 80)
    print("files:")
    for file in workspace.list_files():
        print(file)


if __name__ == "__main__":
    main()