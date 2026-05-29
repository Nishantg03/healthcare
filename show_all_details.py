#!/usr/bin/env python3
"""Show full API response with all criteria details including gaps."""
import requests
import json

case_id = "PA-001"
url = "http://localhost:8000/api/analyze"

print("=" * 100)
print("FULL CRITERIA DETAILS TEST")
print("=" * 100)

try:
    # Upload file
    with open(r"c:\Users\nisha\AppData\Local\Temp\healthcare_copilot_current.xlsx", "rb") as f:
        files = {"file": f}
        requests.post("http://localhost:8000/api/upload", files=files, timeout=30)
    
    # Analyze
    response = requests.post(url, json={"case_id": case_id}, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\nANALYSIS RESULT")
        print(f"  Recommendation: {data.get('recommendation')}")
        print(f"  Confidence: {data.get('confidence')}")
        print(f"  Clinical Summary: {data.get('clinical_summary')}")
        
        print(f"\nCRITERIA DETAILS")
        print(f"  Total criteria: {len(data.get('criteria_results', []))}")
        print()
        
        for i, cr in enumerate(data.get('criteria_results', []), 1):
            print(f"  [{i}] {cr.get('criterion')}")
            print(f"      Status: {cr.get('status')}")
            print(f"      Evidence: {cr.get('evidence', 'N/A')}")
            print(f"      Gap: {cr.get('gap', 'N/A')}")
            print()
        
        print(f"SUPPORTING EVIDENCE ({len(data.get('supporting_evidence', []))} items)")
        for i, ev in enumerate(data.get('supporting_evidence', []), 1):
            print(f"  [{i}] {ev}")
        
        print(f"\nMISSING INFORMATION ({len(data.get('missing_information', []))} items)")
        if data.get('missing_information'):
            for i, mi in enumerate(data.get('missing_information', []), 1):
                print(f"  [{i}] {mi}")
        else:
            print(f"  (None identified)")
        
        print(f"\nPROVIDER QUESTIONS ({len(data.get('provider_questions', []))} items)")
        if data.get('provider_questions'):
            for i, pq in enumerate(data.get('provider_questions', []), 1):
                print(f"  [{i}] {pq}")
        else:
            print(f"  (None identified)")
        
        print(f"\nDENIAL RISKS ({len(data.get('denial_risks', []))} items)")
        if data.get('denial_risks'):
            for i, dr in enumerate(data.get('denial_risks', []), 1):
                print(f"  [{i}] {dr}")
        else:
            print(f"  (None identified)")
        
        # Show raw JSON for debugging
        print(f"\n" + "=" * 100)
        print("RAW JSON (for debugging):")
        print(json.dumps(data, indent=2))
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
