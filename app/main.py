
from fastapi import FastAPI,Query

from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router

app = FastAPI(
    title="FastAPI",
    description="FastAPI framework, high performance, easy to learn, fast to code, ready for production",
    version="0.1.0"
)

app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])

@app.get("/")
async def root():
    return {"message": "Hello WorldQQQ"}


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