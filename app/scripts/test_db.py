import asyncio

from sqlalchemy import text

from app.db.session import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT version()"))
        version = result.scalar_one()

        print(version)


asyncio.run(main())