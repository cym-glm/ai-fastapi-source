from app.langgraph_persistence.graph_factory import build_memory_graph
from app.langgraph_persistence.schemas import create_initial_state


def main():
    app = build_memory_graph()

    config = {
        "configurable": {
            "thread_id": "thread_history_demo"
        }
    }

    app.invoke(
        create_initial_state("我的订单 10002 可以退款吗？"),
        config=config,
    )

    history = list(app.get_state_history(config))

    print("checkpoint count:", len(history))
    print("=" * 80)

    for index, snapshot in enumerate(history, start=1):
        print("snapshot:", index)
        print("checkpoint config:", snapshot.config)
        print("next:", snapshot.next)

        values = snapshot.values
        print("intent:", values.get("intent"))
        print("order_id:", values.get("order_id"))
        print("order_status:", values.get("order_status"))
        print("final_answer:", values.get("final_answer"))
        print("-" * 80)


if __name__ == "__main__":
    main()