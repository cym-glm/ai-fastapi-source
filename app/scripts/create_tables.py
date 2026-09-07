import asyncio

from app.db.init_db import init_db


async def main():
    await init_db()
    print("数据库初始化完成")

asyncio.run(main())