#!/usr/bin/env python3
"""Check what the Excel parser extracts from the file."""
import sys
sys.path.insert(0, 'backend')

from app.services.excel_parser import ExcelParser

print("=" * 100)
print("CHECKING EXCEL PARSER OUTPUT")
print("=" * 100)

try:
    parser = ExcelParser(r"c:\Users\nisha\AppData\Local\Temp\healthcare_copilot_current.xlsx")
    case_data = parser.get_case_data("PA-001")
    
    print("\nExtracted Case Data:")
    print("-" * 100)
    
    case_input = case_data.get("case_input", {})
    
    print(f"\nCase Input Keys: {list(case_input.keys())}")
    print(f"\nCase Input Content:")
    for key, value in case_input.items():
        if isinstance(value, list):
            print(f"  {key}: [{len(value)} items] {value[:2] if len(value) > 0 else []}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n\nApproval Criteria: {len(case_data.get('approval_criteria', []))} items")
    for i, cr in enumerate(case_data.get('approval_criteria', []), 1):
        print(f"  [{i}] {cr.get('criterion', 'N/A')}")
        print(f"      Requirement: {cr.get('requirement', 'N/A')}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
