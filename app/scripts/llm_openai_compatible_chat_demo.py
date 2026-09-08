import asyncio

import httpx

from app.core.config import settings


async def main():
    if not settings.deepseek_api_key:
        raise RuntimeError("请先在.env 中配置 DEEPSEEK_API_KEY")

    url = f"{settings.deepseek_base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    # Chat Completions 风格

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的 AI Agent 课程助教。",
            },
            {
                "role": "user",
                "content": "请用一句话解释什么是 AI Agent。",
            },
        ],
        "temperature": 0.7,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            url,
            headers=headers,
            json=payload,
        )

    print("status_code:", response.status_code)
    print("response:")
    print(response.text)

    if response.status_code == 200:
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        print("answer:", answer)
        print("usage:", usage)


asyncio.run(main())