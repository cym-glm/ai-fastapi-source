from app.deepagents_context.service import deepagents_context_service


def main():
    deepagents_context_service.clear_workspace()

    result = deepagents_context_service.run_demo(
        user_goal=(
            "继续生成第 50 章｜DeepAgents Context 管理，"
            "要求包含概念、代码、FastAPI 接口、面试话术和课后任务。"
        ),
        user_id="u_10001",
        max_tokens=2600,
    )

    print("user_goal:")
    print(result["user_goal"])

    print("=" * 80)
    print("total_estimated_tokens:")
    print(result["context_pack"]["total_estimated_tokens"])

    print("=" * 80)
    print("active_items:")
    for item in result["context_pack"]["active_items"]:
        print(
            item["item_id"],
            item["source"],
            item["priority"],
            item["placement"],
            item["title"],
        )

    print("=" * 80)
    print("offloaded_items:")
    for item in result["context_pack"]["offloaded_items"]:
        print(item["title"], item["file_path"])

    print("=" * 80)
    print("dropped_items:")
    for item in result["context_pack"]["dropped_items"]:
        print(item["title"])

    print("=" * 80)
    print("warnings:")
    for item in result["context_pack"]["warnings"]:
        print("-", item)

    print("=" * 80)
    print("files:")
    for file in result["files"]:
        print(file)

    print("=" * 80)
    print("prompt_preview:")
    print(result["prompt_preview"][:2500])


if __name__ == "__main__":
    main()