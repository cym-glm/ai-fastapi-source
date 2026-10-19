from app.deepagents_intro.workspace import SimpleWorkspace


def main():
    workspace = SimpleWorkspace(
        "data/deepagents_workspace"
    )

    workspace.write_file(
        "research_notes.md",
        "# 研究笔记\n\n这里保存调研过程中的资料。",
    )

    workspace.append_file(
        "research_notes.md",
        "\n\n## 新增资料\n\nAI Agent 平台通常包含 RAG、工具调用、工作流编排和评估能力。",
    )

    print("files:", workspace.list_files())
    print("=" * 80)
    print(workspace.read_file("research_notes.md"))


if __name__ == "__main__":
    main()