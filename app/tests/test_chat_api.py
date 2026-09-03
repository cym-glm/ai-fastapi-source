

import requests

url = "http://127.0.0.1:8000/api/v1/chat"

payload = {
    "message": "AI Agent",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "stream": False,
}

response = requests.post(url, json=payload)

print(response.json())
print(response.status_code)