from app.deepagents_context.memory import memory_store


def main():
    user_id = "u_10001"

    memory_store.add_preference(
        user_id,
        "用户偏好：生成报告时要口语化，适合课程讲解。",
    )
    memory_store.add_preference(
        user_id,
        "用户偏好：代码要能直接运行，并提供测试脚本。",
    )
    memory_store.add_project_term(
        user_id,
        "项目术语：RAG 企业知识库包含 Chunk、Embedding、Retrieval、Evaluation。",
    )
    memory_store.add_project_term(
        user_id,
        "项目术语：DeepAgent 包含 Planning、Sub-Agent、Context 管理。",
    )

    query = "继续生成 DeepAgent Context 管理章节，要求有代码和脚本。"

    memories = memory_store.select_relevant_memories(
        user_id=user_id,
        query=query,
    )

    print("query:", query)
    print("=" * 80)
    print("selected memories:")
    for item in memories:
        print("-", item)


if __name__ == "__main__":
    main()