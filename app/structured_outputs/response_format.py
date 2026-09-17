# 给LLM Provide 的 response_format

from pydantic import BaseModel

# json mode  
def build_json_object_response_format() -> dict:
    # 构建 JSON 对象响应格式
    return {
        "type": "json_object",  # 指定响应类型为 JSON 对象
    }

# json_schema mode
def build_json_schema_response_format(
    schema: type[BaseModel],
    name: str,
    strict: bool = True,
) -> dict:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "strict": strict,
            "schema": schema.model_json_schema(),
        },
    }