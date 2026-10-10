from langgraph.checkpoint.postgres import PostgresSaver

from app.langgraph_persistence.graph_factory import build_persistence_graph
from app.langgraph_persistence.schemas import create_initial_state


DB_URI = "postgresql://postgres:sohucw@localhost:5432/ai_agent?sslmode=disable"


def main():
    config = {
        "configurable": {
            "thread_id": "thread_postgres_demo_001"
        }
    }

    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        # 第一次使用时需要执行 setup。
        # 生产环境不要每次请求都执行，可以放到启动脚本或迁移流程里。
        checkpointer.setup()

        app = build_persistence_graph(
            checkpointer=checkpointer,
        )

        result = app.invoke(
            create_initial_state("我的订单 10002 可以退款吗？"),
            config=config,
        )

        print("final_answer:")
        print(result["final_answer"])

        snapshot = app.get_state(config)

        print("=" * 80)
        print("checkpoint config:")
        print(snapshot.config)


if __name__ == "__main__":
    main()