import asyncio

import httpx


async def main():
    url = "http://127.0.0.1:8000/api/v1/chat/stream"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": "dev-api-key-123",
        "x-user-id": "u_10001",
        "x-username": "dawei",
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": "请用三句话解释为什么 AI Chat 需要流式输出。",
            }
        ],
        "model": "deepseek-chat",
        "temperature": 0.7,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            url,
            headers=headers,
            json=payload,
        ) as response:
            print("status_code:", response.status_code)

            async for line in response.aiter_lines():
                if line:
                    print(line)


if __name__ == "__main__":
    asyncio.run(main())