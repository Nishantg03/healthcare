#!/usr/bin/env python3
"""Test new API key and list available models."""
import os
from dotenv import load_dotenv
import httpx

load_dotenv('backend/.env')
api_key = os.getenv('GROQ_API_KEY')

print(f"API Key: {api_key[:30]}...")
print("\nFetching available models...\n")

headers = {'Authorization': f'Bearer {api_key}'}
resp = httpx.get('https://api.groq.com/openai/v1/models', headers=headers, timeout=30)
data = resp.json()
models = data.get('data', [])

print(f"Available models ({len(models)} total):\n")
for model in models:
    print(f"  • {model.get('id')}")

# Test each model
print("\n" + "="*80)
print("TESTING MODELS")
print("="*80 + "\n")

for model in models[:5]:
    model_id = model.get('id')
    print(f"Testing: {model_id}...", end=" ")
    
    try:
        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            print("✅ WORKS")
        else:
            error = resp.json().get('error', {})
            msg = error.get('message', 'Unknown error')
            print(f"❌ {msg[:60]}")
    except Exception as e:
        print(f"❌ {str(e)[:60]}")
