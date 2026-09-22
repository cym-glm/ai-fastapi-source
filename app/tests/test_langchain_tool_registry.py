import pytest

from langchain_core.tools import BaseTool

from app.langchain_tools.registry import LangChainToolRegistry


class StubTool(BaseTool):
    """测试用桩工具，仅用于向注册表填充 name，不会真正执行。"""

    name: str = "stub_tool"
    description: str = "测试桩工具"

    def _run(self, query: str) -> str:
        return "ok"


def make_tool(name: str) -> BaseTool:
    """创建指定名称的桩工具实例。"""
    return StubTool(name=name, description=f"测试桩工具：{name}")


@pytest.fixture()
def registry() -> LangChainToolRegistry:
    """每个测试用例提供全新的空注册表，避免用例间相互影响。"""
    return LangChainToolRegistry()


class TestNames:
    """测试 LangChainToolRegistry.names 方法"""

    def test_names_empty_registry_returns_empty_list(self, registry):
        """边界值：空注册表应返回空列表"""
        result = registry.names()

        assert result == []
        assert isinstance(result, list)

    def test_names_single_tool(self, registry):
        """正常场景：注册一个工具后应返回只含该工具名的列表"""
        registry.register(make_tool("query_order"))

        result = registry.names()

        assert result == ["query_order"]

    def test_names_multiple_tools_in_insertion_order(self, registry):
        """正常场景：注册多个工具后应按插入顺序返回全部工具名"""
        expected_names = ["query_order", "query_logistics", "transfer_human"]
        for name in expected_names:
            registry.register(make_tool(name))

        result = registry.names()

        assert result == expected_names

    def test_names_with_unicode_tool_name(self, registry):
        """特殊值：工具名包含中文等特殊字符时应原样返回"""
        registry.register(make_tool("查询订单-工具"))

        result = registry.names()

        assert result == ["查询订单-工具"]

    def test_names_deduplicates_when_same_name_registered_twice(self, registry):
        """边界场景：重复注册同名工具（覆盖同一个 key）时不应出现重复名称"""
        registry.register(make_tool("query_order"))
        registry.register(make_tool("query_order"))

        result = registry.names()

        assert result == ["query_order"]
        assert len(result) == len(set(result))

    def test_names_returns_independent_copy(self, registry):
        """返回值应是快照副本：修改返回的列表不应影响注册表内部状态"""
        registry.register(make_tool("query_order"))

        result = registry.names()
        result.append("hacked_name")

        assert registry.names() == ["query_order"]
        assert "hacked_name" not in registry.names()

    def test_names_reflects_state_on_each_call(self, registry):
        """每次调用都应基于注册表当前状态返回最新结果"""
        assert registry.names() == []

        registry.register(make_tool("query_order"))
        assert registry.names() == ["query_order"]

        registry.register(make_tool("transfer_human"))
        assert registry.names() == ["query_order", "transfer_human"]

    def test_names_elements_are_str(self, registry):
        """返回列表中的每个元素都应是 str 类型"""
        registry.register(make_tool("query_order"))
        registry.register(make_tool("query_logistics"))

        result = registry.names()

        assert all(isinstance(name, str) for name in result)
