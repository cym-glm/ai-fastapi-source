from app.langgraph_persistence.graph_factory import build_memory_graph
from app.langgraph_persistence.schemas import create_initial_state


def run_once(app, thread_id: str, question: str):
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = app.invoke(
        create_initial_state(question),
        config=config,
    )

    print("thread_id:", thread_id)
    print("question:", question)
    print("intent:", result["intent"])
    print("order_id:", result["order_id"])
    print("final_answer:", result["final_answer"])
    print("=" * 80)


def main():
    app = build_memory_graph()

    run_once(
        app,
        "thread_user_a",
        "我的订单 10002 可以退款吗？",
    )

    run_once(
        app,
        "thread_user_b",
        "我的订单 10001 可以退款吗？",
    )


if __name__ == "__main__":
    main()