from app.langgraph_persistence.graph_factory import build_memory_graph
from app.langgraph_persistence.schemas import create_initial_state


def main():
    app = build_memory_graph()

    config = {
        "configurable": {
            "thread_id": "thread_update_state_demo"
        }
    }

    app.invoke(
        create_initial_state("我要退款，但是忘记订单号了。"),
        config=config,
    )

    before = app.get_state(config)

    print("before:")
    print(before.values)

    print("=" * 80)

    updated_config = app.update_state(
        config,
        {
            "order_id": "10002",
            "logs": ["manual_update：人工补充 order_id=10002"],
        },
    )

    print("updated_config:")
    print(updated_config)

    print("=" * 80)

    after = app.get_state(config)

    print("after:")
    print(after.values)


if __name__ == "__main__":
    main()