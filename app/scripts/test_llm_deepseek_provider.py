import asyncio

from app.llm.providers.deepseek import DeepSeekProvider
from app.llm.schemas import LLMMessage, LLMRequest, LLMRole


async def main():
    provider = DeepSeekProvider()

    request = LLMRequest(
        model="deepseek-chat",
        messages=[
            LLMMessage(
                role=LLMRole.SYSTEM,
                content="你是一个专业的 AI Agent 课程助教。",
            ),
            LLMMessage(
                role=LLMRole.USER,
                content="请用一句话解释什么是 LLM Provider。",
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