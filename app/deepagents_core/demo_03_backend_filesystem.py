from app.deepagents_core.backend import LocalFilesystemDeepAgentBackend


def main():
    backend = LocalFilesystemDeepAgentBackend(
        root_dir="data/deepagents_core_workspace_demo"
    )

    thread_id = "thread_demo_001"

    backend.write_file(
        thread_id,
        "/research_notes.md",
        "这里是 DeepAgents 研究笔记。",
    )

    backend.write_file(
        thread_id,
        "/draft_report.md",
        "# DeepAgents 报告草稿\n\n这里是草稿。",
    )

    print("files:")
    print(backend.list_files(thread_id))

    print("=" * 80)
    print("research_notes:")
    print(
        backend.read_file(
            thread_id,
            "/research_notes.md",
        )
    )


if __name__ == "__main__":
    main()