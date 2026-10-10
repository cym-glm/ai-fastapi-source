import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import AIMessage, AIMessageChunk

from app.langchain_models.langchain_provider import LangChainLLMProvider
from app.llm.schemas import (
    LLMMessage,
    LLMRole,
    LLMRequest,
    LLMProviderName,
    LLMStreamChunk,
)


class TestLangChainLLMProviderInit:
    """测试 LangChainLLMProvider 类的初始化"""

    def test_init_with_default_values(self):
        """测试使用默认参数初始化"""
        provider = LangChainLLMProvider()

        assert provider.provider == "deepseek"
        assert provider.model == "deepseek-chat"

    def test_init_with_custom_values(self):
        """测试使用自定义参数初始化"""
        provider = LangChainLLMProvider(provider="qwen", model="qwen-plus")

        assert provider.provider == "qwen"
        assert provider.model == "qwen-plus"

    def test_init_with_openai_provider(self):
        """测试使用 openai provider 初始化"""
        provider = LangChainLLMProvider(provider="openai", model="gpt-4o")

        assert provider.provider == "openai"
        assert provider.model == "gpt-4o"


class TestProviderNameProperty:
    """测试 provider_name 属性"""

    def test_provider_name_deepseek(self):
        """测试 deepseek provider 返回正确的枚举值"""
        provider = LangChainLLMProvider(provider="deepseek")
        assert provider.provider_name == LLMProviderName.DEEPSEEK

    def test_provider_name_qwen(self):
        """测试 qwen provider 返回正确的枚举值"""
        provider = LangChainLLMProvider(provider="qwen")
        assert provider.provider_name == LLMProviderName.QWEN

    def test_provider_name_openai(self):
        """测试 openai provider 返回正确的枚举值"""
        provider = LangChainLLMProvider(provider="openai")
        assert provider.provider_name == LLMProviderName.OPENAI

    def test_provider_name_unknown_returns_mock(self):
        """测试未知 provider 返回 MOCK 枚举值"""
        provider = LangChainLLMProvider(provider="unknown")
        assert provider.provider_name == LLMProviderName.MOCK

    def test_provider_name_empty_string(self):
        """测试空字符串 provider 返回 MOCK 枚举值"""
        provider = LangChainLLMProvider(provider="")
        assert provider.provider_name == LLMProviderName.MOCK


def create_test_request(
    model: str = "deepseek-chat",
    messages: list[LLMMessage] | None = None,
    temperature: float = 0.7,
    tools: list[dict] | None = None,
) -> LLMRequest:
    """创建测试用的 LLMRequest 对象"""
    if messages is None:
        messages = [
            LLMMessage(role=LLMRole.USER, content="Hello, how are you?"),
        ]
    return LLMRequest(
        model=model,
        messages=messages,
        temperature=temperature,
        tools=tools,
    )


def create_mock_ai_message(
    content: str = "I am doing well, thank you!",
    usage_metadata: dict | None = None,
    tool_calls: list | None = None,
    response_metadata: dict | None = None,
) -> AIMessage:
    """创建模拟的 AIMessage 对象"""
    if usage_metadata is None:
        usage_metadata = {
            "input_tokens": 10,
            "output_tokens": 20,
            "total_tokens": 30,
        }
    if response_metadata is None:
        response_metadata = {}

    return AIMessage(
        content=content,
        usage_metadata=usage_metadata,
        tool_calls=tool_calls,
        response_metadata=response_metadata,
    )


class TestChatMethod:
    """测试 chat 方法"""

    @pytest.mark.asyncio
    async def test_chat_basic(self):
        """测试基本的非流式聊天"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request()

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=create_mock_ai_message())
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            response = await provider.chat(request)

        assert response.provider == LLMProviderName.DEEPSEEK
        assert response.model == "deepseek-chat"
        assert response.content == "I am doing well, thank you!"
        assert response.usage.prompt_tokens == 10
        assert response.usage.completion_tokens == 20
        assert response.usage.total_tokens == 30

    @pytest.mark.asyncio
    async def test_chat_with_custom_model(self):
        """测试使用自定义模型名称"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request(model="deepseek-reasoner")

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=create_mock_ai_message())
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ) as mock_create:
            response = await provider.chat(request)

        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["model"] == "deepseek-reasoner"
        assert response.model == "deepseek-reasoner"

    @pytest.mark.asyncio
    async def test_chat_with_custom_temperature(self):
        """测试使用自定义温度参数"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request(temperature=0.5)

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=create_mock_ai_message())
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ) as mock_create:
            await provider.chat(request)

        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["temperature"] == 0.5

    @pytest.mark.asyncio
    async def test_chat_with_tools(self):
        """测试带工具调用的聊天"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather information",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ]
        request = create_test_request(tools=tools)

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=create_mock_ai_message())
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            await provider.chat(request)

        mock_model.bind_tools.assert_called_once_with(tools)

    @pytest.mark.asyncio
    async def test_chat_with_tool_calls_in_response(self):
        """测试响应中包含工具调用"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request()

        tool_calls = [
            {
                "id": "call_123",
                "name": "get_weather",
                "args": {"location": "Beijing"},
            }
        ]
        mock_ai_message = create_mock_ai_message(
            content="Let me check the weather for you.",
            tool_calls=tool_calls,
        )

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=mock_ai_message)
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            response = await provider.chat(request)

        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].id == "call_123"
        assert response.tool_calls[0].name == "get_weather"

    @pytest.mark.asyncio
    async def test_chat_with_empty_content(self):
        """测试空内容响应"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request()

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=create_mock_ai_message(content=""))
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            response = await provider.chat(request)

        assert response.content == ""

    @pytest.mark.asyncio
    async def test_chat_with_none_content(self):
        """测试 None 内容响应"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request()

        mock_ai_message = create_mock_ai_message()
        mock_ai_message.content = None

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=mock_ai_message)
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            response = await provider.chat(request)

        assert response.content == ""

    @pytest.mark.asyncio
    async def test_chat_with_finish_reason(self):
        """测试带有 finish_reason 的响应"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request()

        mock_ai_message = create_mock_ai_message(
            response_metadata={"finish_reason": "stop"},
        )

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=mock_ai_message)
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            response = await provider.chat(request)

        assert response.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_chat_with_qwen_provider(self):
        """测试 qwen provider"""
        provider = LangChainLLMProvider(provider="qwen", model="qwen-plus")
        request = create_test_request()

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=create_mock_ai_message())
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            response = await provider.chat(request)

        assert response.provider == LLMProviderName.QWEN

    @pytest.mark.asyncio
    async def test_chat_with_openai_provider(self):
        """测试 openai provider"""
        provider = LangChainLLMProvider(provider="openai", model="gpt-4o")
        request = create_test_request()

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=create_mock_ai_message())
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            response = await provider.chat(request)

        assert response.provider == LLMProviderName.OPENAI

    @pytest.mark.asyncio
    async def test_chat_with_multiple_messages(self):
        """测试多轮对话"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content="You are a helpful assistant."),
            LLMMessage(role=LLMRole.USER, content="Hello!"),
            LLMMessage(role=LLMRole.ASSISTANT, content="Hello! How can I help you?"),
            LLMMessage(role=LLMRole.USER, content="What's the weather?"),
        ]
        request = create_test_request(messages=messages)

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=create_mock_ai_message())
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            response = await provider.chat(request)

        assert response.content == "I am doing well, thank you!"

    @pytest.mark.asyncio
    async def test_chat_streaming_false(self):
        """测试 streaming=False 参数传递"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request()

        mock_model = MagicMock()
        mock_model.ainvoke = AsyncMock(return_value=create_mock_ai_message())
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ) as mock_create:
            await provider.chat(request)

        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["streaming"] is False


class TestStreamChatMethod:
    """测试 stream_chat 方法"""

    @pytest.mark.asyncio
    async def test_stream_chat_basic(self):
        """测试基本的流式聊天"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request()

        chunks = [
            AIMessageChunk(content="Hello"),
            AIMessageChunk(content="Hello, world"),
            AIMessageChunk(content="Hello, world!"),
        ]
        for i, chunk in enumerate(chunks):
            chunk.id = f"chunk-{i}"
            chunk.response_metadata = {"finish_reason": "stop"} if i == len(chunks) - 1 else {}

        mock_model = MagicMock()
        mock_model.astream = MagicMock(return_value=AsyncIteratorMock(chunks))

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            result_chunks = []
            async for chunk in provider.stream_chat(request):
                result_chunks.append(chunk)

        assert len(result_chunks) == 3
        assert result_chunks[0].content == "Hello"
        assert result_chunks[1].content == "Hello, world"
        assert result_chunks[2].content == "Hello, world!"

    @pytest.mark.asyncio
    async def test_stream_chat_with_custom_model(self):
        """测试流式聊天使用自定义模型"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request(model="deepseek-reasoner")

        mock_model = MagicMock()
        mock_model.astream = MagicMock(return_value=AsyncIteratorMock([]))

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ) as mock_create:
            async for _ in provider.stream_chat(request):
                pass

        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["model"] == "deepseek-reasoner"

    @pytest.mark.asyncio
    async def test_stream_chat_with_custom_temperature(self):
        """测试流式聊天使用自定义温度"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request(temperature=0.3)

        mock_model = MagicMock()
        mock_model.astream = MagicMock(return_value=AsyncIteratorMock([]))

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ) as mock_create:
            async for _ in provider.stream_chat(request):
                pass

        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["temperature"] == 0.3

    @pytest.mark.asyncio
    async def test_stream_chat_streaming_true(self):
        """测试 streaming=True 参数传递"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request()

        mock_model = MagicMock()
        mock_model.astream = MagicMock(return_value=AsyncIteratorMock([]))

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ) as mock_create:
            async for _ in provider.stream_chat(request):
                pass

        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["streaming"] is True

    @pytest.mark.asyncio
    async def test_stream_chat_with_provider_name(self):
        """测试流式响应中包含正确的 provider"""
        provider = LangChainLLMProvider(provider="qwen", model="qwen-plus")
        request = create_test_request()

        chunk = AIMessageChunk(content="Streaming content")
        chunk.id = "chunk-1"
        chunk.response_metadata = {}

        mock_model = MagicMock()
        mock_model.astream = MagicMock(return_value=AsyncIteratorMock([chunk]))

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            result_chunks = []
            async for chunk in provider.stream_chat(request):
                result_chunks.append(chunk)

        assert all(c.provider == LLMProviderName.QWEN for c in result_chunks)

    @pytest.mark.asyncio
    async def test_stream_chat_empty_response(self):
        """测试空流式响应"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request()

        mock_model = MagicMock()
        mock_model.astream = MagicMock(return_value=AsyncIteratorMock([]))

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            result_chunks = []
            async for chunk in provider.stream_chat(request):
                result_chunks.append(chunk)

        assert len(result_chunks) == 0

    @pytest.mark.asyncio
    async def test_stream_chat_with_none_content(self):
        """测试流式响应内容为 None"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request()

        chunk = AIMessageChunk(content=None)
        chunk.id = "chunk-1"
        chunk.response_metadata = {}

        mock_model = MagicMock()
        mock_model.astream = MagicMock(return_value=AsyncIteratorMock([chunk]))

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            result_chunks = []
            async for chunk in provider.stream_chat(request):
                result_chunks.append(chunk)

        assert len(result_chunks) == 1
        assert result_chunks[0].content == ""

    @pytest.mark.asyncio
    async def test_stream_chat_raw_chunk_structure(self):
        """测试流式响应的 raw_chunk 结构"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")
        request = create_test_request()

        chunk = AIMessageChunk(content="Test content")
        chunk.id = "test-id-123"
        chunk.response_metadata = {"key": "value"}

        mock_model = MagicMock()
        mock_model.astream = MagicMock(return_value=AsyncIteratorMock([chunk]))

        with patch(
            "app.langchain_models.langchain_provider.LangChainModelFactory.create",
            return_value=mock_model,
        ):
            result_chunks = []
            async for chunk in provider.stream_chat(request):
                result_chunks.append(chunk)

        assert len(result_chunks) == 1
        assert result_chunks[0].raw_chunk["id"] == "test-id-123"
        assert result_chunks[0].raw_chunk["content"] is None  # Original chunk content
        assert result_chunks[0].raw_chunk["response_metadata"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_stream_chat_with_multiple_providers(self):
        """测试不同 provider 的流式响应"""
        providers_and_expected = [
            ("deepseek", "deepseek-chat", LLMProviderName.DEEPSEEK),
            ("qwen", "qwen-plus", LLMProviderName.QWEN),
            ("openai", "gpt-4o-mini", LLMProviderName.OPENAI),
        ]

        for provider_name, model_name, expected_enum in providers_and_expected:
            provider = LangChainLLMProvider(provider=provider_name, model=model_name)
            request = create_test_request()

            chunk = AIMessageChunk(content="Test")
            chunk.id = "chunk-1"
            chunk.response_metadata = {}

            mock_model = MagicMock()
            mock_model.astream = MagicMock(return_value=AsyncIteratorMock([chunk]))

            with patch(
                "app.langchain_models.langchain_provider.LangChainModelFactory.create",
                return_value=mock_model,
            ):
                async for result_chunk in provider.stream_chat(request):
                    assert result_chunk.provider == expected_enum


class TestToStreamChunk:
    """测试 _to_stream_chunk 方法"""

    def test_to_stream_chunk_basic(self):
        """测试基本的流式块转换"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")

        chunk = AIMessageChunk(content="Hello")
        chunk.id = "test-id"
        chunk.response_metadata = {"finish_reason": "stop"}

        result = provider._to_stream_chunk(chunk=chunk, model="deepseek-chat")

        assert isinstance(result, LLMStreamChunk)
        assert result.provider == LLMProviderName.DEEPSEEK
        assert result.model == "deepseek-chat"
        assert result.content == "Hello"
        assert result.finish_reason is None  # _to_stream_chunk always sets finish_reason to None
        assert result.usage == LLMUsage()
        assert result.raw_chunk["id"] == "test-id"
        assert result.raw_chunk["content"] is None  # Original chunk content
        assert result.raw_chunk["response_metadata"] == {"finish_reason": "stop"}

    def test_to_stream_chunk_empty_content(self):
        """测试空内容转换"""
        provider = LangChainLLMProvider(provider="qwen", model="qwen-plus")

        chunk = AIMessageChunk(content="")
        chunk.id = "chunk-1"
        chunk.response_metadata = {}

        result = provider._to_stream_chunk(chunk=chunk, model="qwen-plus")

        assert result.content == ""

    def test_to_stream_chunk_none_content(self):
        """测试 None 内容转换"""
        provider = LangChainLLMProvider(provider="openai", model="gpt-4o")

        chunk = AIMessageChunk(content=None)
        chunk.id = "chunk-2"
        chunk.response_metadata = {}

        result = provider._to_stream_chunk(chunk=chunk, model="gpt-4o")

        assert result.content == ""

    def test_to_stream_chunk_with_custom_model(self):
        """测试使用自定义模型名称"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")

        chunk = AIMessageChunk(content="Test")
        chunk.id = "id-1"
        chunk.response_metadata = {}

        result = provider._to_stream_chunk(chunk=chunk, model="custom-model")

        assert result.model == "custom-model"

    def test_to_stream_chunk_preserves_response_metadata(self):
        """测试保留 response_metadata"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")

        metadata = {
            "finish_reason": "stop",
            "custom_key": "custom_value",
            "usage": {"total_tokens": 100},
        }
        chunk = AIMessageChunk(content="Content")
        chunk.id = "id-1"
        chunk.response_metadata = metadata

        result = provider._to_stream_chunk(chunk=chunk, model="deepseek-chat")

        assert result.raw_chunk["response_metadata"] == metadata

    def test_to_stream_chunk_different_providers(self):
        """测试不同 provider 的转换"""
        test_cases = [
            ("deepseek", LLMProviderName.DEEPSEEK),
            ("qwen", LLMProviderName.QWEN),
            ("openai", LLMProviderName.OPENAI),
            ("unknown", LLMProviderName.MOCK),
        ]

        for provider_str, expected_enum in test_cases:
            provider = LangChainLLMProvider(provider=provider_str, model="test-model")
            chunk = AIMessageChunk(content="Test")
            chunk.id = "id"
            chunk.response_metadata = {}

            result = provider._to_stream_chunk(chunk=chunk, model="test-model")

            assert result.provider == expected_enum

    def test_to_stream_chunk_usage_is_empty(self):
        """测试 usage 是空的 LLMUsage"""
        provider = LangChainLLMProvider(provider="deepseek", model="deepseek-chat")

        chunk = AIMessageChunk(content="Test")
        chunk.id = "id"
        chunk.response_metadata = {}

        result = provider._to_stream_chunk(chunk=chunk, model="deepseek-chat")

        assert result.usage.prompt_tokens == 0
        assert result.usage.completion_tokens == 0
        assert result.usage.total_tokens == 0


class AsyncIteratorMock:
    """用于模拟异步迭代器的辅助类"""

    def __init__(self, items: list):
        self.items = items
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item
