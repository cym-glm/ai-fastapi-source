import asyncio

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.langgraph_persistence.graph_factory import build_persistence_graph
from app.langgraph_persistence.schemas import create_initial_state


DB_URI = "postgresql://postgres:sohucw@localhost:5432/ai_agent?sslmode=disable"


async def main():
    config = {
        "configurable": {
            "thread_id": "thread_async_postgres_demo_002"
        }
    }

    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
        # 第一次使用时需要执行 setup。
        # 生产环境建议放到启动初始化或部署迁移流程中。
        await checkpointer.setup()

        app = build_persistence_graph(
            checkpointer=checkpointer,
        )

        result = await app.ainvoke(
            create_initial_state("我的订单 10002 可以退款吗？"),
            config=config,
        )

        print("final_answer:")
        print(result["final_answer"])

        snapshot = await app.aget_state(config)

        print("=" * 80)
        print("checkpoint config:")
        print(snapshot.config)


if __name__ == "__main__":
    asyncio.run(main())