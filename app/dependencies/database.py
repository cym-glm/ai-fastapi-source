from collections.abc import AsyncGenerator

class MockDBSession:
    async def execute(self, sql: str)->str:
        return f"执行sql：{sql}，返回结果"
    async def close(self):
        print("关闭数据库连接")


async def get_db_session() -> AsyncGenerator[MockDBSession, None]:
    db = MockDBSession()
    try:
        yield db
    finally:
        await db.close()



# async def test():
#         db = MockDBSession()
#         return db;