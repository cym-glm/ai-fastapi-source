
from fastapi import APIRouter, HTTPException
router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "service": "ai-fastapi-course"}



@router.get("/error")
async def error_demo():
    raise HTTPException(status_code=400, detail="这是一个错误的示例")
