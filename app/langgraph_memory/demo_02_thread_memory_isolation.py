from langchain_core.messages import HumanMessage

from app.langgraph_memory.demo_01_short_term_memory import build_graph


def run_chat(app, thread_id: str, content: str):
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=content)
            ]
        },
        config=config,
    )

    print("thread_id:", thread_id)
    print("message_count:", len(result["messages"]))
    for message in result["messages"]:
        print(message.type, ":", message.content)
        
    print("=" * 80)


def main():
    app = build_graph()

    run_chat(app, "thread_user_a", "我叫用户 A。")
    run_chat(app, "thread_user_b", "我叫用户 B。")
    run_chat(app, "thread_user_a", "你还记得我是谁吗？")
    run_chat(app, "thread_user_b", "你还记得我是谁吗？")


if __name__ == "__main__":
    main()