from langchain_core.tools import BaseTool

from app.langchain_tools.tools import ECOMMERCE_LANGCHAIN_TOOLS


class LangChainToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"工具不存在：{name}")

        return self._tools[name]

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def get_many(
        self,
        names: list[str] | None = None,
    ) -> list[BaseTool]:
        if not names:
            return self.list()

        return [
            self.get(name)
            for name in names
        ]


langchain_tool_registry = LangChainToolRegistry()


for item in ECOMMERCE_LANGCHAIN_TOOLS:
    langchain_tool_registry.register(item)



# 电商客服对话助手
#   query_order query_logistics transfer_human
# RAG场景--- search_knowlege
# Agent 场景 --- 
#数据分析： query_db 
# 