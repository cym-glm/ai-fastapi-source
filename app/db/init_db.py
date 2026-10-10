

from app.db.base import Base
from app.db.session import engine

# 导入模型模块，以便在初始化数据库时创建表结构
# from app import models

from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)