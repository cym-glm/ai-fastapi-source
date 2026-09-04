
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.chat import SourceDocument, TokenUsage

#  
class RAGQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="用户问题")
    # 查询的知识库 ID，对应于知识库的唯一标识
    knowledge_base_id: str = Field(..., description="知识库 ID")
    # 召回文档数量，默认为5个 
    top_k: int = Field(default=5, ge=1, le=20, description="召回文档数量")
    # 是否开启重排，默认为 True
    rerank: bool = Field(default=True, description="是否开启重排")
    metadata_filter: dict[str, Any] = Field(default_factory=dict, description="元数据过滤条件")


class RAGQueryResponse(BaseModel):
    answer: str = Field(..., description="AI 回答")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    sources: list[SourceDocument] = Field(default_factory=list, description="引用来源")
    usage: TokenUsage = Field(default_factory=TokenUsage, description="Token 用量")
    trace_id: str | None = Field(default=None, description="链路追踪 ID")
