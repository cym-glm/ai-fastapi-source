
from fastapi import APIRouter, HTTPException, Depends
from app.core.config import Settings
from app.dependencies.settings import get_app_settins
router = APIRouter()


async def get_request_source() -> str:
    return "我有一个请求源"

# @router.get("/health")
# async def health(source: str = Depends(get_request_source)):
#     return {"status": "ok", "version": "1.0.0", "service": "ai-fastapi-course", "source": source}

@router.get("/health")
async def health(settings: Settings = Depends(get_app_settins), source: str = Depends(get_request_source)):
    return {"status": "ok", "version": "1.0.0", "service": "ai-fastapi-course", "source": source, "env": settings.app_env}


@router.get("/error")
async def error_demo():
    raise HTTPException(status_code=400, detail="这是一个错误的示例")

@router.get("/system-error-demo")
async def system_error_demo():
    result = 1 / 0
    return {
        "result": result
    }