from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class ChatMemoryState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def chat_node(state: ChatMemoryState) -> dict:
    last_message = state["messages"][-1]

    history_count = len(state["messages"])

    return {
        "messages": [
            AIMessage(
                content=(
                    f"我收到了：{last_message.content}。"
                    f"当前 thread 里一共有 {history_count} 条历史消息。"
                )
            )
        ]
    }


def build_graph():
    graph = StateGraph(ChatMemoryState)

    graph.add_node("chat", chat_node)

    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)

    checkpointer = InMemorySaver()

    return graph.compile(checkpointer=checkpointer)


def main():
    app = build_graph()

    config = {
        "configurable": {
            "thread_id": "thread_chat_memory_demo"
        }
    }

    first = app.invoke(
        {
            "messages": [
                HumanMessage(content="我叫大伟。")
            ]
        },
        config=config,
    )

    print("first:")
    for message in first["messages"]:
        print(message.type, ":", message.content)

    print("=" * 80)

    second = app.invoke(
        {
            "messages": [
                HumanMessage(content="你还记得我刚才说了什么吗？")
            ]
        },
        config=config,
    )

    print("second:")
    for message in second["messages"]:
        print(message.type, ":", message.content)


if __name__ == "__main__":
    main()