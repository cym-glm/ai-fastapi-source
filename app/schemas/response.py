from typing import Generic, Any, TypeVar

from pydantic import BaseModel,Field

T = TypeVar("T")
class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(default=200, description="业务状态码")
    message: str = Field(default="success", description="提示消息")
    data: T | None = Field(default=None, description="返回数据")


class ErrorResponse(BaseModel):
    code: int = Field(default=500, description="错误码")
    message: str = Field(default="error", description="错误消息")
    detail: str | None = Field(default=None, description="错误详情")

# {
#   "code": 400,
#   "message": "Bad Request",
#   "detail": "具体错误"
# }