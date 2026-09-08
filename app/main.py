
from fastapi import FastAPI,Query

# from app.api.v1.chat import router as chat_router
# from app.api.v1.health import router as health_router
# from app.api.v1.conversations import router as conversation_router
# from app.api.v1.rag import router as rag_router
from contextlib import asynccontextmanager
from app.redis.client import close_redis
from app.api.v1.api import api_router as chat_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import register_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("应用启动")
    yield
    print("应用关闭")
    await close_redis()

def create_app() -> FastAPI:
    # 初始化日志配置
    setup_logging()
    app = FastAPI(
        title= settings.app_name,
        description="FastAPI framework, high performance, easy to learn, fast to code, ready for production",
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # 注册中间件
    register_middleware(app)
    # 注册异常处理
    register_exception_handlers(app)

    app.include_router(chat_router, prefix=settings.api_v1_prefix)
    # app.include_router(chat_router, prefix=settings.api_v1_prefix, tags=["chat"])
    # app.include_router(health_router, prefix=settings.api_v1_prefix, tags=["health"])
    # app.include_router(conversation_router, prefix=settings.api_v1_prefix, tags=["conversations"])
    # app.include_router(rag_router, prefix=settings.api_v1_prefix, tags=["rag"])

    @app.get("/")
    async def root():
        return {"message": settings.app_name, "version": settings.app_version, "env": settings.app_env}


    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        return {
                "id": user_id,
                "name": f"User {user_id}"
        }

    @app.get("/search")
    async def search(
        q: str = Query(..., min_length=1, max_length=50, description="Query string"),
        page: int = Query(default=1, ge=1, description="age number"),
        size: int = Query(default=10, ge=1, le=100, description="Page size"),
    ):
        return {
            "q": q,
            "page": page,
            "size": size
        }

    return app

app = create_app()



