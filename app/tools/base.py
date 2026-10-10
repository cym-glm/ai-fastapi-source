import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel, Field


ToolCallable = Callable[..., Awaitable[BaseModel] | BaseModel]


class ToolDefinition(BaseModel):
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    args_schema: type[BaseModel] = Field(..., description="参数 Schema")
    result_schema: type[BaseModel] = Field(..., description="结果 Schema")
    func: ToolCallable = Field(..., description="工具函数")
    enabled: bool = Field(default=True, description="是否启用")
    require_confirm: bool = Field(default=False, description="是否需要人工确认")

    class Config:
        arbitrary_types_allowed = True

    def to_openai_tool(self) -> dict:
        schema = self.args_schema.model_json_schema()

        schema.setdefault("additionalProperties", False)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema,
            },
        }

    async def execute(self, arguments: dict[str, Any]) -> BaseModel:
        validated_args = self.args_schema.model_validate(arguments)

        if inspect.iscoroutinefunction(self.func):
            return await self.func(**validated_args.model_dump())

        result = self.func(**validated_args.model_dump())

        if inspect.isawaitable(result):
            return await result

        return result