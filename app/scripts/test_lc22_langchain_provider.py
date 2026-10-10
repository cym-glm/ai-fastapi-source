import asyncio

from app.langchain_models.langchain_provider import LangChainLLMProvider
from app.llm.schemas import LLMMessage, LLMRequest, LLMRole


async def main():
    provider = LangChainLLMProvider(
        provider="deepseek",
        model="deepseek-chat",
    )

    request = LLMRequest(
        model="deepseek-chat",
        messages=[
            LLMMessage(
                role=LLMRole.SYSTEM,
                content="你是一个专业 AI Agent 课程助教。",
            ),
            LLMMessage(
                role=LLMRole.USER,
                content="请用三句话解释 LangChainLLMProvider 的作用。",
            ),
        ],
        temperature=0.7,
        stream=False,
    )

    response = await provider.chat(request)

    print("content:")
    print(response.content)
    print("=" * 80)
    print("usage:")
    print(response.usage.model_dump())
    print("=" * 80)
    print("raw_response:")
    print(response.raw_response)


if __name__ == "__main__":
    asyncio.run(main())