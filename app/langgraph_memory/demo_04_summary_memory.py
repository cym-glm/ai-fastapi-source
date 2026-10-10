from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class SummaryMemoryState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    short_summary: str | None
    final_answer: str


def summarize_if_needed_node(state: SummaryMemoryState) -> dict:
    messages = state["messages"]

    if len(messages) < 6:
        return {
            "short_summary": state.get("short_summary"),
        }

    old_text = "\n".join(
        f"{message.type}: {message.content}"
        for message in messages[:-4]
    )

    # 教学版：这里用简单拼接模拟摘要。
    # 真实项目里应该调用总结模型。
    summary = (
        "早期对话摘要：用户提到过自己叫大伟，"
        "正在学习 LangGraph，并且想做电商客服 Agent。"
        f"\n原始摘要依据：{old_text[:120]}..."
    )

    return {
        "short_summary": summary
    }


def answer_node(state: SummaryMemoryState) -> dict:

    summary = state.get("short_summary") or "暂无摘要"
    
    recent_messages = state["messages"][-4:]

    recent_text = "\n".join(
        f"{message.type}: {message.content}"
        for message in recent_messages
    )

    answer = (
        "我会结合摘要和最近消息回答。\n\n"
        f"【摘要】{summary}\n\n"
        f"【最近消息】\n{recent_text}"
    )

    return {
        "messages": [
            AIMessage(content=answer)
        ],
        "final_answer": answer,
    }


def build_graph():
    graph = StateGraph(SummaryMemoryState)

    graph.add_node("summarize_if_needed", summarize_if_needed_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "summarize_if_needed")
    graph.add_edge("summarize_if_needed", "answer")
    graph.add_edge("answer", END)

    checkpointer = InMemorySaver()

    return graph.compile(checkpointer=checkpointer)


def main():
    app = build_graph()

    config = {
        "configurable": {
            "thread_id": "thread_summary_memory_demo"
        }
    }

    questions = [
        "我叫大伟。",
        "我正在学习 LangGraph。",
        "我想做电商客服 Agent。",
        "我希望回答口语化一点。",
        "我还想要代码完整。",
        "请你总结一下你记住了什么。",
    ]

    for question in questions:
        result = app.invoke(
            {
                "messages": [
                    HumanMessage(content=question)
                ],
                "short_summary": None,
                "final_answer": "",
            },
            config=config,
        )

        print("question:", question)
        print("summary:", result["short_summary"])
        print("final_answer:", result["final_answer"][:300])
        print("=" * 80)


if __name__ == "__main__":
    main()