#!/usr/bin/env python3
"""Check why LLM is rate limited."""
import os
import sys
import json
import httpx
from dotenv import load_dotenv

# Load env
load_dotenv('backend/.env')

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

print("=" * 80)
print("GROQ API STATUS CHECK")
print("=" * 80)
print(f"\nAPI Key configured: {'✓' if api_key else '✗ MISSING'}")
if api_key:
    print(f"API Key (first 20): {api_key[:20]}...")
print(f"Model: {model}")

if not api_key:
    print("\n❌ ERROR: GROQ_API_KEY not configured!")
    sys.exit(1)

print("\n" + "=" * 80)
print("TESTING API CALL")
print("=" * 80)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": model,
    "messages": [
        {
            "role": "system",
            "content": "You are a test. Respond with 'OK'."
        },
        {
            "role": "user",
            "content": "Test message"
        }
    ],
    "max_tokens": 50
}

try:
    print(f"\nCalling: https://api.groq.com/openai/v1/chat/completions")
    print(f"Model: {model}")
    
    response = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30.0
    )
    
    print(f"\n✓ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        result = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"✓ Response: {result[:100]}")
    else:
        print(f"\n❌ Status: {response.status_code}")
        body = response.json()
        error = body.get("error", {})
        print(f"Error Type: {error.get('type')}")
        print(f"Error Code: {error.get('code')}")
        print(f"Error Message: {error.get('message')}")
        
        # Extract details
        msg = error.get('message', '')
        if 'rate_limit' in msg.lower():
            print("\n📊 RATE LIMIT DETAILS:")
            print(f"  {msg}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()
