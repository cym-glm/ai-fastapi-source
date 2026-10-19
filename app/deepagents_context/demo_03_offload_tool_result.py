from dataclasses import asdict

from app.deepagents_context.context_manager import DeepAgentContextManager
from app.deepagents_context.workspace import ContextWorkspace


def main():
    workspace = ContextWorkspace(
        "data/deepagents_context_workspace_demo_03"
    )
    workspace.clear()

    manager = DeepAgentContextManager(
        workspace=workspace
    )

    long_content = "\n".join([
        f"第 {index} 条搜索结果：这是非常长的工具结果，应该写入 workspace，而不是全部放进 messages。"
        for index in range(1, 60)
    ])

    item = manager.offload_to_file(
        title="长搜索结果",
        content=long_content,
        directory="/tool_results",
    )

    print("context item:")
    print(asdict(item))

    print("=" * 80)
    print("files:")
    print(workspace.list_files())

    print("=" * 80)
    print("file content preview:")
    print(workspace.read_file(item.file_path)[:500])


if __name__ == "__main__":
    main()