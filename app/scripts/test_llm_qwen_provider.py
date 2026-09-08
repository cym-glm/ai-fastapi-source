import asyncio

from app.llm.providers.qwen import QwenProvider
from app.llm.schemas import LLMMessage, LLMRequest, LLMRole


async def main():
    provider = QwenProvider()

    request = LLMRequest(
        model="qwen-plus",
        messages=[
            LLMMessage(
                role=LLMRole.SYSTEM,
                content="你是一个专业的 AI Agent 课程助教。",
            ),
            LLMMessage(
                role=LLMRole.USER,
                content="请用一句话解释什么是统一 LLM Provider 架构。",
            ),
        ],
        temperature=0.7,
        stream=False,
    )

    response = await provider.chat(request)

    print("provider:", response.provider)
    print("model:", response.model)
    print("content:", response.content)
    print("usage:", response.usage.model_dump())


if __name__ == "__main__":
    asyncio.run(main())