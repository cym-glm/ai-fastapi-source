
from langchain_core.messages import AIMessage, HumanMessage

from langgraph.graph import MessagesState, END, START, StateGraph


def assit_node(state: MessagesState) -> dict:
    last_message = state["messages"][-1]
    return {
        "messages": [AIMessage(content=f"我收到你的消息了：{last_message.content}")]
    }


def build_graph():
    graph = StateGraph(MessagesState)

    graph.add_node("assit", assit_node)
    graph.add_edge(START, "assit")
    graph.add_edge("assit", END)
    return graph.compile()


def main():
    app = build_graph()
    res = app.invoke({
        "messages": [
            HumanMessage(content="你是谁"),
        ]
    })
    for msg in res["messages"]:
        print(msg.type, ": ", msg.content)


if __name__ == "__main__":
    main()
