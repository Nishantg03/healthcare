
"""Test analyze endpoint with detailed error tracing."""
import requests
import json
import sys

case_id = "PA-001"
url = "http://localhost:8000/api/analyze"

print("=" * 80)
print("DETAILED API TEST")
print("=" * 80)

# First upload file
print("\n[Step 1] Upload file...")
try:
    with open(r"c:\Users\nisha\AppData\Local\Temp\healthcare_copilot_current.xlsx", "rb") as f:
        files = {"file": f}
        upload_response = requests.post(
            "http://localhost:8000/api/upload",
            files=files,
            timeout=30
        )
    print(f"  Upload status: {upload_response.status_code}")
except Exception as e:
    print(f"  Upload error: {e}")

# Now analyze
print("\n[Step 2] Call analyze endpoint...")
try:
    payload = {"case_id": case_id}
    
    # Use verbose requests to see what's happening
    response = requests.post(
        url,
        json=payload,
        timeout=60  # Longer timeout for LLM calls
    )
    
    print(f"  Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n[Step 3] Response Data:")
        print(f"  Recommendation: {data.get('recommendation')}")
        print(f"  Confidence: {data.get('confidence')}")
        print(f"  Clinical Summary: {data.get('clinical_summary')}")
        
        # Check if it's the rate limit message
        summary = data.get('clinical_summary', '')
        if 'rate limited' in summary.lower():
            print(f"\n⚠️  RATE LIMITED DETECTED!")
            print(f"   Message: {summary}")
        elif 'error' in summary.lower():
            print(f"\n❌ ERROR DETECTED!")
            print(f"   Message: {summary}")
        else:
            print(f"\n✓ Analysis successful")
            
        print(f"\n  Criteria:")
        for cr in data.get('criteria_results', []):
            print(f"    - {cr.get('criterion')}: {cr.get('status')}")
            
        print(f"\n  Supporting Evidence: {len(data.get('supporting_evidence', []))} items")
        print(f"  Missing Information: {len(data.get('missing_information', []))} items")
    else:
        print(f"  Error response: {response.text[:300]}")
        
except requests.Timeout:
    print("  Request timeout (>60s) - backend may be slow")
except Exception as e:
    print(f"  Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("To see backend errors, check the backend console output or logs")
print("=" * 80)
