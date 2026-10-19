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
        "data/deepagents_subagent_workspace_demo_03"
    )
    workspace.clear()

    registry = SubAgentRegistry(
        specs=build_default_subagent_specs(),
        tool_executor=SubAgentToolExecutor(
            build_subagent_tools()
        ),
    )

    context = """
        Research 结果：
        Dify 偏 AI 应用编排；
        Coze 偏低门槛 Bot 搭建；
        LangGraph 偏开发者可控编排。

        Analysis 结果：
        企业 Agent 平台需要 RAG、工具调用、权限、日志和评估。
        """

    writer_result = registry.run(
        agent_name="writer-agent",
        instruction="根据资料写 AI Agent 平台调研报告。",
        input_context=context,
        expected_output="输出 Markdown 报告。",
        write_file=workspace.write_file,
    )

    reviewer_result = registry.run(
        agent_name="reviewer-agent",
        instruction="审查报告质量。",
        input_context=writer_result.output,
        expected_output="输出审查意见。",
        write_file=workspace.write_file,
    )

    print("writer:")
    print(asdict(writer_result))

    print("=" * 100)
    print("reviewer:")
    print(asdict(reviewer_result))

    print("=" * 80)
    print("files:")
    for file in workspace.list_files():
        print(file)


if __name__ == "__main__":
    main()