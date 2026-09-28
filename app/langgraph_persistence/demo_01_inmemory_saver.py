from app.langgraph_persistence.graph_factory import build_memory_graph

from app.langgraph_persistence.schemas import create_initial_state


def main():
    app = build_memory_graph()

    config = {
        "configurable": {
            "thread_id": "thread_lg34_demo_001"
        }
    }

    result = app.invoke(
        create_initial_state("我的订单 10002 可以退款吗？"),
        config= config,
    )

    print("final_answer:")
    print(result["final_answer"])

    print("=" * 80)
    print("logs:")
    for log in result["logs"]:
        print("-", log)



if __name__ == "__main__":
    main()