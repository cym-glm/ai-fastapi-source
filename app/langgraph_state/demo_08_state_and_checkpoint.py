from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class UserProfileState(TypedDict):
    user_name: str | None
    favorite_topic: str | None
    answer: str


def remember_name_node(state: UserProfileState) -> dict:
    if state.get("user_name"):
        return {
            "answer": f"我记住你的名字了：{state['user_name']}"
        }

    return {
        "answer": "你还没有告诉我你的名字。"
    }


def remember_topic_node(state: UserProfileState) -> dict:
    if state.get("favorite_topic"):
        return {
            "answer": (
                f"我记住了，你关注的话题是：{state['favorite_topic']}。"
            )
        }

    return {}


def build_graph():
    graph = StateGraph(UserProfileState)

    graph.add_node("remember_name", remember_name_node)
    graph.add_node("remember_topic", remember_topic_node)

    graph.add_edge(START, "remember_name")
    graph.add_edge("remember_name", "remember_topic")
    graph.add_edge("remember_topic", END)

    # 设置 checkpoint
    checkpointer = InMemorySaver()

    return graph.compile(checkpointer=checkpointer)


def main():
    app = build_graph()

    config = {
        "configurable": {
            "thread_id": "state_checkpoint_demo"
        }
    }

    first_result = app.invoke(
        {
            "user_name": "大伟",
            "favorite_topic": None,
            "answer": "",
        },
        config=config,
    )

    print("first_result:")
    print(first_result)

    second_result = app.invoke(
        {
            "favorite_topic": "LangGraph State 设计",
        },
        config=config,
    )

    print("second_result:")
    print(second_result)


if __name__ == "__main__":
    main()

