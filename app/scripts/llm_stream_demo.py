import asyncio
import json

import httpx

from app.core.config import settings


async def main():
    if not settings.deepseek_api_key:
        raise RuntimeError("请先在 .env 中配置 DEEPSEEK_API_KEY")

    url = f"{settings.deepseek_base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": "请用三句话解释什么是 AI Agent。",
            }
        ],
        "temperature": 0.7,
        "stream": True,
    }

    full_answer = ""

    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream(
            "POST",
            url,
            headers=headers,
            json=payload,
        ) as response:
            print("status_code:", response.status_code)

            async for line in response.aiter_lines():
                if not line:
                    continue
                # data: {"choices": [{"delta": {"content": "AI Agent 是指一种能够自主地与环境交互、学习和适应的智能体。"}, "index": 0, "finish_reason": null}]}
                if not line.startswith("data:"):
                    continue

                data = line.removeprefix("data:").strip()

                # data:[DONE]
                if data == "[DONE]":
                    break

                chunk = json.loads(data)

                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content")

                if content:
                    full_answer += content
                    print(content, end="", flush=True)

    print("\n\nfull_answer:")
    print(full_answer)


asyncio.run(main())