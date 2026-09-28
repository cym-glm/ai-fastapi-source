from app.langgraph_persistence.graph_factory import build_memory_graph
from app.langgraph_persistence.schemas import create_initial_state


def main():
    app = build_memory_graph()

    config = {
        "configurable": {
            "thread_id": "thread_get_state_demo"
        }
    }

    app.invoke(
        create_initial_state("我的订单 10002 可以退款吗？"),
        config=config,
    )

    snapshot = app.get_state(config)

    print("snapshot values:")
    print(snapshot.values)

    print("=" * 80)
    print("next:")
    print(snapshot.next)

    print("=" * 80)
    print("config:")
    print(snapshot.config)


if __name__ == "__main__":
    main()