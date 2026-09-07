from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal

class MockDBSession:
    async def execute(self, sql: str)->str:
        return f"执行sql：{sql}，返回结果"
    async def close(self):
        print("关闭数据库连接")


async def get_db_session() -> AsyncGenerator[MockDBSession, None]:
    # db = MockDBSession()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()



# async def test():
#         db = MockDBSession()
#         return db;