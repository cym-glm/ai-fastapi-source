from app.deepagents_core.service import deep_agent_core_service


def main():
    response_1 = deep_agent_core_service.run_task(
        user_request="帮我调研 DeepAgents 核心架构。",
        tenant_id="tenant_001",
        user_id="u_10001",
        thread_id="thread_user_001",
    )

    response_2 = deep_agent_core_service.run_task(
        user_request="帮我调研 RAG 企业知识库架构。",
        tenant_id="tenant_001",
        user_id="u_10002",
        thread_id="thread_user_002",
    )

    print("thread 1:")
    print("thread_id:", response_1["thread_id"])
    print("files:", response_1["files"])

    print("=" * 80)

    print("thread 2:")
    print("thread_id:", response_2["thread_id"])
    print("files:", response_2["files"])


if __name__ == "__main__":
    main()