#!/usr/bin/env python3
"""List all cases available in the Excel file."""
import pandas as pd

excel_file = r"c:\Users\nisha\AppData\Local\Temp\healthcare_copilot_current.xlsx"

print("=" * 80)
print("AVAILABLE CASES IN EXCEL FILE")
print("=" * 80)

try:
    xls = pd.ExcelFile(excel_file)
    print(f"\nSheets in workbook: {xls.sheet_names}\n")
    
    # Read the case input sheet
    df = pd.read_excel(excel_file, sheet_name="Case Input")
    
    print(f"Cases found:")
    for idx, row in df.iterrows():
        if pd.notna(row.get("Case ID")):
            case_id = row.get("Case ID")
            patient_age = row.get("Patient Age", "?")
            diagnosis = row.get("Primary Diagnosis", "?")
            print(f"  - {case_id}: Age {patient_age}, {diagnosis}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
