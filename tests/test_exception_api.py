import requests


BASE_URL = "http://127.0.0.1:8000"


def print_response(response):
    print("status_code:", response.status_code)
    print("headers x-trace-id:", response.headers.get("x-trace-id"))
    print("json:", response.json())


def test_missing_api_key():
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": "什么是 AI Agent？"
                }
            ],
            "model": "deepseek-chat",
            "temperature": 0.7,
            "stream": False
        }
    )

    print_response(response)


def test_validation_error():
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        headers={
            "x-api-key": "dev-api-key-123",
            "x-user-id": "u_10001",
            "x-username": "dawei",
        },
        json={
            "messages": [],
            "model": "deepseek-chat",
            "temperature": 3,
            "stream": False
        }
    )

    print_response(response)


def test_business_error():
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        headers={
            "x-api-key": "dev-api-key-123",
            "x-user-id": "u_10001",
            "x-username": "dawei",
        },
        json={
            "messages": [
                {
                    "role": "user",
                    "content": "触发业务异常"
                }
            ],
            "model": "deepseek-chat",
            "temperature": 0.7,
            "stream": False
        }
    )

    print_response(response)


def test_system_error():
    response = requests.get(
        f"{BASE_URL}/api/v1/system-error-demo"
    )

    print_response(response)


print("====== missing api key ======")
test_missing_api_key()

print("====== validation error ======")
test_validation_error()

print("====== business error ======")
test_business_error()

print("====== system error ======")
test_system_error()