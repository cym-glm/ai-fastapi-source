import asyncio
import json

import httpx


BASE_URL = "http://127.0.0.1:8000/api/v1"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": "dev-api-key-123",
    "x-user-id": "ux_10001",
    "x-username": "dawei",
}


async def main():
    async with httpx.AsyncClient(timeout=120) as client:
        conversation_id = await create_conversation(client)

        await chat_once(
            client=client,
            conversation_id=conversation_id,
            question="请用1句话解释什么是 AI Agent。",
        )

        await chat_once(
            client=client,
            conversation_id=conversation_id,
            question="请用1句话解释什么是 AI Agent。",
        )

        await chat_with_tools(
            client=client,
            conversation_id=conversation_id,
        )

        await get_messages(
            client=client,
            conversation_id=conversation_id,
        )


async def create_conversation(client: httpx.AsyncClient) -> str:
    response = await client.post(
        f"{BASE_URL}/conversations",
        headers=HEADERS,
        json={
            "title": "项目一完整联调"
        },
    )

    data = response.json()
    print("create_conversation:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    return data["data"]["conversation_id"]


async def chat_once(
    client: httpx.AsyncClient,
    conversation_id: str,
    question: str,
):
    response = await client.post(
        f"{BASE_URL}/chat",
        headers=HEADERS,
        json={
            "session_id": conversation_id,
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ],
            "model": "deepseek-chat",
            "temperature": 0.7,
            "stream": False,
            "prompt_scenario": "general_chat",
        },
    )

    data = response.json()
    print("chat:")
    print(json.dumps(data, ensure_ascii=False, indent=2))


async def chat_with_tools(
    client: httpx.AsyncClient,
    conversation_id: str,
):
    response = await client.post(
        f"{BASE_URL}/chat",
        headers=HEADERS,
        json={
            "session_id": conversation_id,
            "messages": [
                {
                    "role": "user",
                    "content": "帮我查一下订单 10001 到哪了？",
                }
            ],
            "model": "deepseek-chat",
            "temperature": 0.3,
            "stream": False,
            "prompt_scenario": "ecommerce_customer_service",
            "metadata": {
                "business_rules": "不能编造物流信息；没有订单号时必须先引导用户提供订单号。",
                "order_info": "用户提供了订单号 10001。",
            },
        },
    )

    data = response.json()
    print("chat_with_tools:")
    print(json.dumps(data, ensure_ascii=False, indent=2))


async def get_messages(
    client: httpx.AsyncClient,
    conversation_id: str,
):
    response = await client.get(
        f"{BASE_URL}/conversations/{conversation_id}/messages",
        headers=HEADERS,
    )

    data = response.json()
    print("messages:")
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())