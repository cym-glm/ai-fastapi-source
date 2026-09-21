import asyncio

from app.langchain_demo.06_compare_with_native  import (
    langchain_version,
    native_version,
)


async def main():
    native_answer = await native_version()
    print("native answer:")
    print(native_answer)

    print("=" * 80)

    langchain_answer = langchain_version()
    print("langchain answer:")
    print(langchain_answer)


if __name__ == "__main__":
    asyncio.run(main())