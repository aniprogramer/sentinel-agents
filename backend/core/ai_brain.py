import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
KIMI_API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.moonshot.cn/v1/chat/completions"

def call_kimi(prompt: str, schema: dict, temperature: float = 0.2):
    headers = {
        "Authorization": f"Bearer {KIMI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "moonshot-v1-8k",   # or moonshot-v1-32k depending on tier
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": "You are Sentinel, an autonomous AI security auditor. Always return valid JSON strictly matching the schema."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        return {"error": f"JSON parsing failed: {str(e)}"}
