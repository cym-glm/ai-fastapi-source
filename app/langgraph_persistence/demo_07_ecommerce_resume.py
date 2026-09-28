from langgraph.checkpoint.memory import InMemorySaver

from app.langgraph_persistence.graph_factory import (
    add_user_message_to_state,
    build_persistence_graph,
)
from app.langgraph_persistence.schemas import create_initial_state


def main():
    checkpointer = InMemorySaver()

    app = build_persistence_graph(
        checkpointer=checkpointer,
    )

    config = {
        "configurable": {
            "thread_id": "thread_ecommerce_resume_demo"
        }
    }

    first_result = app.invoke(
        create_initial_state("我要退款。"),
        config=config,
    )

    print("first_result:")
    print("final_answer:", first_result["final_answer"])
    print("intent:", first_result["intent"])
    print("need_user_input:", first_result["need_user_input"])
    print("waiting_for:", first_result["waiting_for"])
    print("order_id:", first_result["order_id"])
    print("=" * 80)

    second_result = app.invoke(
        add_user_message_to_state("订单号是 10002。"),
        config=config,
    )

    print("second_result:")
    print("final_answer:", second_result["final_answer"])
    print("intent:", second_result["intent"])
    print("need_user_input:", second_result["need_user_input"])
    print("waiting_for:", second_result["waiting_for"])
    print("order_id:", second_result["order_id"])
    print("order_status:", second_result["order_status"])

    print("=" * 80)
    print("messages:")
    for message in second_result["messages"]:
        print(message.type, ":", message.content)

    print("=" * 80)
    print("logs:")
    for log in second_result["logs"]:
        print("-", log)


if __name__ == "__main__":
    main()