from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph


class ConfigNodeState(TypedDict):
    user_question: str
    order_id: str | None
    final_answer: str


def extract_order_id_node(state: ConfigNodeState) -> dict:
    if "10001" in state["user_question"]:
        return {"order_id": "10001"}

    return {"order_id": None}


def query_order_node(
    state: ConfigNodeState,
    config: RunnableConfig,
) -> dict:
    configurable = config.get("configurable", {})

    user_id = configurable.get("user_id", "unknown")
    trace_id = configurable.get("trace_id", "unknown")

    return {
        "final_answer": (
            f"trace_id={trace_id}，"
            f"用户 {user_id} 查询订单 {state['order_id']}。"
            "真实项目这里要做订单归属校验。"
        )
    }


def build_graph():
    graph = StateGraph(ConfigNodeState)

    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("query_order", query_order_node)

    graph.add_edge(START, "extract_order_id")
    graph.add_edge("extract_order_id", "query_order")
    graph.add_edge("query_order", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke(
        {
            "user_question": "帮我查一下订单 10001。",
            "order_id": None,
            "final_answer": "",
        },
        config={
            "configurable": {
                "thread_id": "thread_lg32_config_001",
                "user_id": "u_10001",
                "trace_id": "trace_lg32_abc",
            }
        },
    )

    print(result)


if __name__ == "__main__":
    main()