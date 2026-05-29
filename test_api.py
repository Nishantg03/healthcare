#!/usr/bin/env python3
"""Test the API to see actual response and errors."""
import requests
import json

# Test case
case_id = "PA-001"

print("=" * 80)
print("Testing API")
print("=" * 80)

# Call the analyze endpoint
url = "http://localhost:8000/api/analyze"
payload = {"case_id": case_id}

try:
    print(f"\n[Request] POST {url}")
    print(f"[Payload] {json.dumps(payload)}")
    
    response = requests.post(url, json=payload, timeout=30)
    
    print(f"\n[Response Status] {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n[Response Data]")
        print(f"  Recommendation: {data.get('recommendation')}")
        print(f"  Confidence: {data.get('confidence')}")
        print(f"  Clinical Summary: {data.get('clinical_summary')}")
        print(f"  Criteria Results: {len(data.get('criteria_results', []))} items")
        for cr in data.get('criteria_results', []):
            print(f"    - {cr.get('criterion')}: {cr.get('status')}")
        print(f"  Supporting Evidence: {len(data.get('supporting_evidence', []))} items")
        print(f"  Missing Information: {len(data.get('missing_information', []))} items")
    else:
        print(f"\n[Error Response]")
        print(response.text)
        
except Exception as e:
    print(f"\n[Exception] {e}")
    import traceback
    traceback.print_exc()
