
from typing import Annotated, TypedDict


from langchain_core.messages.utils import (
    count_tokens_approximately,
    trim_messages
)

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class TrimMemoryState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    final_answer: str


def chat_node(state: TrimMemoryState) -> dict:
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=128,
        start_on="human",
        end_on=("ai", "human"),
    )

    answer = (
        f"原始消息数量：{len(state['messages'])}，"
        f"裁剪后消息数量：{len(trimmed_messages)}。"
    )

    return {
        "messages": [
            AIMessage(content=answer)
        ],
        "final_answer": answer,
    }


def build_graph():
    graph = StateGraph(TrimMemoryState)


    graph.add_node("chat", chat_node)

    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)

    checkpointer = InMemorySaver()

    return graph.compile(checkpointer=checkpointer)


def main():
    app = build_graph()

    config = {
        "configurable": {
            "thread_id": "thread_trim_messages_demo"
        }
    }

    questions = [
        "第一轮：我叫大伟。",
        "第二轮：我在学习 LangGraph。",
        "第三轮：我想做电商客服 Agent。",
        "第四轮：我想让回答更口语化。",
        "第五轮：请总结一下你现在记住了什么。",
    ]

    for question in questions:
        result = app.invoke(
            {
                "messages": [HumanMessage(content=question)],
                "final_answer": "",
            },
            config=config,
        )

        print("question:", question)
        print("final_answer:", result["final_answer"])
        print("total_messages:", len(result["messages"]))
        print("=" * 80)


if __name__ == "__main__":
    main()

