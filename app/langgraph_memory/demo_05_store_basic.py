from langgraph.store.memory import InMemoryStore

# sesionstrage  localstorage
def main():
    store = InMemoryStore()

    tenant_id = "tenant_001"
    user_id = "u_10001"

    namespace = (tenant_id, user_id, "preferences")

    store.put(
        namespace,
        "answer_style",
        {
            "type": "preference",
            "content": "用户喜欢口语化、直接、代码完整的回答。",
            "confidence": 0.95,
            "source": "user_explicit_request",
        },
    )

    item = store.get(namespace, "answer_style")

    print("get memory:")
    print(item)

    print("=" * 80)

    items = store.search(namespace)

    print("search memories:")
    for memory in items:
        print("key:", memory.key)
        print("value:", memory.value)
        print("-" * 80)


if __name__ == "__main__":
    main()