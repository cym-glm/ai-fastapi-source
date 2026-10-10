import asyncio
import json

from app.llm.schemas import (
    LLMProviderName,
    LLMResponse,
    LLMToolCall,
    LLMUsage,
)
from app.services.tool_calling_service import ToolCallingService


class FakeProvider:
    def __init__(self) -> None:
        self.requests = []

    async def chat(self, request):
        self.requests.append(request)
        if len(self.requests) == 1:
            return LLMResponse(
                provider=LLMProviderName.DEEPSEEK,
                model="deepseek-chat",
                content="",
                tool_calls=[
                    LLMToolCall(
                        id="call_1",
                        name="get_order_status",
                        arguments={"order_id": "10001"},
                        raw_arguments='{"order_id":"10001"}',
                    )
                ],
                usage=LLMUsage(),
            )

        return LLMResponse(
            provider=LLMProviderName.DEEPSEEK,
            model="deepseek-chat",
            content="订单已发货。",
            usage=LLMUsage(),
        )


def test_second_request_contains_assistant_tool_calls(monkeypatch):
    async def fake_execute(tool_name, arguments):
        class Result:
            def model_dump(self):
                return {"status": "shipped"}

        return Result()

    monkeypatch.setattr(
        "app.services.tool_calling_service.tool_executor.execute",
        fake_execute,
    )
    provider = FakeProvider()

    result = asyncio.run(
        ToolCallingService().run_with_tools(
            user_question="查询订单 10001",
            model="deepseek-chat",
            llm_provider=provider,
        )
    )

    messages = provider.requests[1].messages
    assistant_message = messages[-2]
    tool_message = messages[-1]

    assert assistant_message.tool_calls[0].id == "call_1"
    assert tool_message.tool_call_id == "call_1"
    assert json.loads(tool_message.content)["success"] is True
    assert result["answer"] == "订单已发货。"
