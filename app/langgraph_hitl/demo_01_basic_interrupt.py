from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from langgraph.types import Command, interrupt


class BasicHITLState(TypedDict):
    user_question: str
    final_answer: str


def human_review_node(state: BasicHITLState) -> dict:
    decision = interrupt({
        "type": "human_review",
        "question": state["user_question"],
        "message": "请人工审核这个回答是否可以继续。",
    })

    return {
        "final_answer": f"人工审核结果：{decision}"
    }


def build_graph():
    graph = StateGraph(BasicHITLState)

    graph.add_node("human_review", human_review_node)

    graph.add_edge(START, "human_review")
    graph.add_edge("human_review", END)

    checkpointer = InMemorySaver()

    return graph.compile(checkpointer=checkpointer)


def main():
    app = build_graph()

    config = {
        "configurable": {
            "thread_id": "thread_lg35_basic_interrupt"
        }
    }

    print("第一次执行，会在 interrupt 暂停：")
    
    first = app.invoke(
        {
            "user_question": "请帮我执行一个需要人工审核的动作。",
            "final_answer": "",
        },
        config=config,
    )

    print(first)

    print("=" * 80)
    print("第二次执行，用 Command(resume=...) 恢复：")

    second = app.invoke(
        Command(resume="approve"),
        config=config,
    )

    print(second)


if __name__ == "__main__":
    main()