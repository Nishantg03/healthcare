
"""List available Groq models."""
import os
import httpx
from dotenv import load_dotenv
import json

load_dotenv('backend/.env')
api_key = os.getenv("GROQ_API_KEY")

headers = {"Authorization": f"Bearer {api_key}"}

print("Fetching available Groq models...\n")

response = httpx.get(
    "https://api.groq.com/openai/v1/models",
    headers=headers,
    timeout=30.0
)

if response.status_code == 200:
    data = response.json()
    models = data.get("data", [])
    print(f"Available models ({len(models)} total):\n")
    for model in models:
        model_id = model.get("id")
        print(f"  • {model_id}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
