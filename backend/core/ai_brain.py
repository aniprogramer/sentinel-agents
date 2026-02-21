import os
import requests
from dotenv import load_dotenv

load_dotenv()
KIMI_API_KEY = os.getenv("KIMI_API_KEY")

BASE_URL = "https://api.moonshot.cn/v1/chat/completions"

def call_kimi(prompt: str, schema: dict, temperature: float = 0.2):
    headers = {
        "Authorization": f"Bearer {KIMI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "moonshot-v1-8k",  # or moonshot-v1-32k
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": "You are Sentinel, an autonomous AI security auditor. Always return valid JSON strictly matching the schema."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(BASE_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
