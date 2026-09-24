from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class MemoryChatState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def chat_node(state: MemoryChatState) -> dict:
    user_message = state["messages"][-1]

    return {
        "messages": [
            AIMessage(
                content=f"我记住这一轮了：{user_message.content}"
            )
        ]
    }


def build_graph():
    graph = StateGraph(MemoryChatState)

    graph.add_node("chat", chat_node)

    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)

    # 真实业务--数据库持久化
    checkpointer = InMemorySaver()

    return graph.compile(
        checkpointer=checkpointer,
    )


def main():
    app = build_graph()

    config = {
        "configurable": {
            "thread_id": "thread_demo_001"  # user_id + task_id _ conversation_id
        }
    }

    first_result = app.invoke(
        {
            "messages": [
                HumanMessage(content="我叫大伟。")
            ]
        },
        config=config,
    )

    print("first run:")
    for message in first_result["messages"]:
        print(message.type, ":", message.content)

    print("=" * 80)

    second_result = app.invoke(
        {
            "messages": [
                HumanMessage(content="你还记得我刚才说什么吗？")
            ]
        },
        config=config,
    )

    print("second run:")
    for message in second_result["messages"]:
        print(message.type, ":", message.content)


if __name__ == "__main__":
    main()