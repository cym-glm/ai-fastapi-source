from langgraph.types import Command

from app.langgraph_hitl.graph_factory import build_memory_hitl_graph
from app.langgraph_hitl.schemas import create_initial_state


def main():
    app = build_memory_hitl_graph()

    config = {
        "configurable": {
            "thread_id": "thread_lg35_stream_interrupt"
        }
    }

    print("第一次 stream，观察 interrupt:")
    print("=" * 80)

    for chunk in app.stream(
        create_initial_state("我的订单 10003 申请退款。"),
        config=config,
        stream_mode="updates",
    ):
        print(chunk)

    print("=" * 80)
    print("恢复执行:")
    print("=" * 80)

    for chunk in app.stream(
        Command(resume={
            "type": "approve",
            "reviewer_id": "admin_001",
            "reason": "人工审核通过",
        }),
        config=config,
        stream_mode="updates",
    ):
        print(chunk)


if __name__ == "__main__":
    main()