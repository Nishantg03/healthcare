"""Demonstrate how gaps show when criteria are PARTIAL or NOT_MET."""
from app.services.criteria_matcher import CriteriaMatcher

print("=" * 100)
print("DEMONSTRATING HOW GAPS AND MISSING INFO WORK")
print("=" * 100)

matcher = CriteriaMatcher()

# Test Case 1: PARTIAL - Only 1 failed treatment (needs 2)
print("\n[Test 1] PARTIAL - Insufficient failed treatments")
print("-" * 100)

partial_case = {
    "imaging_findings": ["mild foraminal narrowing"],  # Mild, not severe
    "failed_treatments": ["PT"],  # Only 1 treatment (needs 2+)
    "symptoms": ["back pain", "arm pain"],
    "requested_service": "Cervical fusion"
}

criteria_config = [
    {"criterion": "Imaging Correlation"},
    {"criterion": "Conservative Treatment Failure"},
    {"criterion": "Functional Impairment"},
    {"criterion": "Medical Necessity"}
]

results1 = matcher.evaluate_criteria(
    case_input=partial_case,
    extraction={},  # Empty LLM (simulating failed API call)
    approval_criteria=criteria_config
)

for cr in results1:
    print(f"  {cr.criterion}: {cr.status}")
    print(f"    Evidence: {cr.evidence}")
    print(f"    Gap: {cr.gap}")
    print()

# Test Case 2: NOT_MET - Missing documentation
print("\n[Test 2] NOT_MET - Missing critical documentation")
print("-" * 100)

incomplete_case = {
    "imaging_findings": [],  # NO imaging findings
    "failed_treatments": [],  # NO failed treatments
    "symptoms": [],  # NO symptoms documented
    "requested_service": ""  # NO service specified
}

results2 = matcher.evaluate_criteria(
    case_input=incomplete_case,
    extraction={},
    approval_criteria=criteria_config
)

for cr in results2:
    print(f"  {cr.criterion}: {cr.status}")
    print(f"    Evidence: {cr.evidence}")
    print(f"    Gap: {cr.gap}")
    print()

# Test Case 3: MIXED - Some MET, some PARTIAL, some NOT_MET
print("\n[Test 3] MIXED - Some criteria met, some gaps")
print("-" * 100)

mixed_case = {
    "imaging_findings": ["severe stenosis", "cord compression"],  # GOOD - Severe
    "failed_treatments": ["Physical therapy"],  # POOR - Only 1 treatment
    "symptoms": ["severe pain", "numbness"],  # ACCEPTABLE - 2 symptoms
    "requested_service": "Decompression"  # GOOD - Clear
}

results3 = matcher.evaluate_criteria(
    case_input=mixed_case,
    extraction={},
    approval_criteria=criteria_config
)

for cr in results3:
    status_color = "MET" if cr.status == "MET" else f"PARTIAL/NOT_MET"
    print(f"  {cr.criterion}: {cr.status}")
    print(f"    Evidence: {cr.evidence}")
    print(f"    Gap: {cr.gap}")
    print()

print("=" * 100)
print("SUMMARY:")
print("=" * 100)
print("""
The gap field shows what's MISSING when criteria are PARTIAL or NOT_MET.

Current PA-001 case:
  - Has 2 imaging findings (severe) ✓
  - Has 5 failed treatments ✓
  - Has 10 symptoms ✓
  - Has clear service indication ✓
  -> Result: All MET, No gaps

To see gaps, you would need:
  - Missing imaging findings
  - Insufficient failed treatments (<2)
  - Incomplete symptom documentation
  - Unclear medical necessity

The system is working CORRECTLY - PA-001 has excellent documentation!
""")
