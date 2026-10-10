from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def assistant_node(state: ChatState) -> dict:
    last_message = state["messages"][-1]

    return {
        "messages": [
            AIMessage(
                content=f"我收到你的问题了：{last_message.content}"
            )
        ]
    }


def build_graph():
    graph = StateGraph(ChatState)

    graph.add_node("assistant", assistant_node)

    graph.add_edge(START, "assistant")
    graph.add_edge("assistant", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke({
        "messages": [
            HumanMessage(content="LangGraph 的 add_messages 是什么？")
        ]
    })

    for message in result["messages"]:
        print(message.type, ":", message.content)


if __name__ == "__main__":
    main()