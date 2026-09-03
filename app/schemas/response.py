from typing import Any

from pydantic import BaseModel,Field

class ApiResponse(BaseModel):
    code: int = Field(default=200, description="业务状态码")
    message: str = Field(default="success", description="提示消息")
    data: Any = Field(default=None, description="返回数据")

