from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph


class ConfigState(TypedDict):
    user_question: str
    answer: str


def answer_node(
    state: ConfigState,
    config: RunnableConfig,
) -> dict:
    configurable = config.get("configurable", {})

    user_id = configurable.get("user_id", "unknown")
    tenant_id = configurable.get("tenant_id", "unknown")
    trace_id = configurable.get("trace_id", "unknown")

    return {
        "answer": (
            f"用户 {user_id} 来自租户 {tenant_id}，"
            f"trace_id={trace_id}，"
            f"问题是：{state['user_question']}"
        )
    }


def build_graph():
    graph = StateGraph(ConfigState)

    graph.add_node("answer", answer_node)

    graph.add_edge(START, "answer")
    graph.add_edge("answer", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke(
        {
            "user_question": "RunnableConfig 有什么用？",
            "answer": "",
        },
        config={
            "configurable": {
                "thread_id": "thread_001",
                "user_id": "u_10001",
                "tenant_id": "tenant_001",
                "trace_id": "trace_abc123",
            }
        },
    )

    print(result)


if __name__ == "__main__":
    main()