
import asyncio
import httpx
from app.core.config import settings

async def main():
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI API key is not set, 请在.env文件中设置OPENAI_API_KEY环境变量。")
    url = f"{settings.openai_base_url}/responses"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4.1-mini",
        "input": "请用一句话解释什么是 AI Agent。",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=headers, json=payload)

        print("status_code:", response.status_code)
        print("response:")
        print(response.text)

asyncio.run(main())