import asyncio

from app.llm.factory import LLMProviderFactory
from app.services.structured_output_service import structured_output_service


async def main():
    provider = LLMProviderFactory.create("deepseek")

    result = await structured_output_service.generate_rag_answer(
        user_question="公司年假有几天？",
        retrieved_context="[doc_001] 员工入职满一年后，每年享有 5 天带薪年假。",
        model="deepseek-chat",
        llm_provider=provider,
    )

    print(result.model_dump())


if __name__ == "__main__":
    asyncio.run(main())