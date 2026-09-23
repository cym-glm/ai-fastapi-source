import json

from langchain_core.tools import StructuredTool, tool
from pydantic import BaseModel, Field
from app.langchain_rag.service import langchain_rag_service


class SearchKnowledgeBaseArgs(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="用户问题或检索关键词",
    )


async def search_knowledge_base(query: str) -> str:
    """
    搜索企业知识库，并返回基于知识库的回答和引用来源。
    """
    result = langchain_rag_service.ask(
        question=query,
        provider="deepseek",
        model_name="deepseek-chat",
        k=4,
    )

    return json.dumps(
        result.model_dump(),
        ensure_ascii=False,
    )


search_knowledge_base_tool = StructuredTool.from_function(
    coroutine=search_knowledge_base,
    name="search_knowledge_base",
    description=(
        "搜索企业知识库。当用户询问公司制度、售后规则、课程阶段、内部文档内容时使用。"
        "如果知识库没有相关内容，应说明无法从知识库确认，不要编造。"
    ),
    args_schema=SearchKnowledgeBaseArgs,
)