# Excel Workbook Structure Guide

This document describes the required structure for Excel workbooks used with the Healthcare Pre-Authorization Copilot.

## Required Sheets

Your Excel workbook **must** contain exactly these 6 sheets:

### 1. Problem_Statement
**Purpose:** Context and case overview (currently ignored during processing)

| Column | Type | Description |
|--------|------|-------------|
| Case_Description | String | Problem description |
| Background | String | Clinical background |

**Example:**
```
Case: Cervical Spine Fusion Surgery Pre-Authorization
Patient: 58-year-old male presenting with progressive cervical myelopathy
```

---

### 2. Training_Cases
**Purpose:** Reference examples for few-shot LLM reasoning

| Column | Required | Type | Description |
|--------|----------|------|-------------|
| PA_ID | Yes | String | Unique case identifier (e.g., "PA-001") |
| symptoms | Yes | String | Comma or semicolon-separated symptoms |
| imaging_findings | Yes | String | Imaging study results |
| failed_treatments | Yes | String | Conservative treatments attempted |
| documentation_gaps | No | String | Areas lacking documentation |
| expected_outcomes | No | String | Expected clinical outcomes |

**Example:**
```
PA_ID: PA-001
symptoms: gait imbalance; hand numbness; grip weakness
imaging_findings: severe stenosis; cord compression; T2 signal change
failed_treatments: physical therapy; NSAIDs; gabapentin
documentation_gaps: ADL impairment weakly documented
expected_outcomes: Pain relief; improved neurologic function
```

**Notes:**
- Use semicolons (;) or commas (,) to separate list items
- Include at least 2-3 training cases for good reasoning
- These are used as context for LLM analysis

---

### 3. Patient_Data_Aspects
**Purpose:** Define the data schema and categories used in the case

| Column | Type | Description |
|--------|------|-------------|
| aspect_category | String | Data category (e.g., "demographics") |
| elements | String | Specific elements in this category |
| examples | String | Example values |

**Example:**
```
Category: Demographics
Elements: age, gender, medical_history
Examples: 58, Male, Type 2 Diabetes

Category: Symptoms
Elements: gait_imbalance, hand_numbness, pain_level
Examples: Present, Absent, 8/10

Category: Imaging
Elements: mri_findings, ct_results, xray_results
Examples: Stenosis, Compression, Normal
```

**Valid Categories:**
- demographics
- symptoms
- imaging
- treatments
- functional_impairment
- documentation_quality
- service_requested
- contraindications

---

### 4. Complex_Case_Input
**Purpose:** The actual patient case to be analyzed

| Column | Required | Type | Description |
|--------|----------|------|-------------|
| PA_ID | Optional | String | Case identifier (defaults to "COMPLEX_CASE") |
| age | Yes | Integer | Patient age |
| gender | Yes | String | M/F/Other |
| requested_service | Yes | String | Procedure/service requested |
| symptoms | Yes | String | List of symptoms |
| imaging_findings | Yes | String | List of imaging results |
| failed_treatments | Yes | String | List of failed treatments |
| documentation_notes | No | String | Clinical notes and documentation |
| medical_history | No | String | Relevant medical history |

**Example:**
```
PA_ID: COMPLEX_CASE
age: 58
gender: Male
requested_service: C5-C6 cervical decompression and fusion
symptoms: gait imbalance; hand numbness; grip weakness; neck pain
imaging_findings: MRI severe stenosis; cord compression; T2 signal change
failed_treatments: PT 6 weeks; NSAIDs 4 weeks; gabapentin 8 weeks; epidural steroid injection
documentation_notes: Patient reports 6-month progression of symptoms. Neurologic exam shows hyperreflexia, positive Hoffman sign. Limited ADL including difficulty with grooming and eating
medical_history: Type 2 Diabetes; Hypertension
```

---

### 5. Complex_Case_Outcome
**Purpose:** Approval criteria and expected evaluation logic

| Column | Required | Type | Description |
|--------|----------|------|-------------|
| criterion_name | Yes | String | Approval criterion |
| description | Yes | String | What must be demonstrated |
| met_status | No | String | MET / PARTIAL / NOT_MET |
| evidence | No | String | Supporting evidence if MET |
| gap | No | String | Gap if NOT_MET or PARTIAL |

**Example:**
```
Criterion: Imaging Correlation
Description: Advanced imaging (MRI/CT) demonstrating structural pathology
Status: MET
Evidence: MRI shows severe C5-C6 stenosis with cord compression
Gap: —

Criterion: Failed Conservative Treatment
Description: Documentation of 2+ weeks conservative treatment
Status: MET
Evidence: PT 6 weeks, NSAIDs 4 weeks, gabapentin 8 weeks, epidural injection
Gap: —

Criterion: Functional Impairment
Description: Clear documentation of ADL limitations
Status: PARTIAL
Evidence: Patient reports difficulty with grooming and eating
Gap: Explicit ADL wording missing, needs formal functional assessment
```

---

### 6. Suggested_Output
**Purpose:** Define the expected response format

| Column | Type | Description |
|--------|------|-------------|
| output_field | String | JSON field name |
| expected_type | String | Data type |
| example_value | String | Example value |

**Example:**
```
output_field: recommendation
expected_type: String (enum)
example_value: LIKELY_APPROVE / LIKELY_DENY / NEED_MORE_INFO

output_field: confidence
expected_type: String (enum)
example_value: HIGH / MEDIUM / LOW

output_field: clinical_summary
expected_type: String
example_value: "58-year-old male with progressive cervical myelopathy..."

output_field: criteria_results
expected_type: Array[Object]
example_value: [{"criterion": "...", "status": "MET", "evidence": "..."}]
```

---

## Tips for Excel Workbook Creation

### ✅ Best Practices

1. **Use consistent formatting**
   - Keep data types consistent (ages as numbers, not text)
   - Use the same separators (; or ,) for lists

2. **Provide complete data**
   - Include all required columns
   - Don't leave critical fields blank

3. **Use realistic examples**
   - Training cases should reflect actual clinical scenarios
   - Match complexity of real pre-auth cases

4. **Document clearly**
   - Use explicit terminology
   - Spell out medical terms fully
   - Avoid abbreviations unless clinically standard

### ❌ Common Issues

| Issue | Solution |
|-------|----------|
| Empty Training_Cases | Add at least 2-3 example cases |
| Missing columns | Check all required columns are present |
| Mixed data formats | Use consistent formatting (all dates same format) |
| Blank required fields | Ensure critical fields have values |
| Special characters | Use standard ASCII, avoid special formatting |

---

## Sample Workbook Template

Download or reference the template structure:

```
Sheet: Training_Cases
│
├─ PA_ID: PA-001
├─ symptoms: symptom list
├─ imaging_findings: findings list
├─ failed_treatments: treatment list
└─ documentation_gaps: gap list

Sheet: Complex_Case_Input
│
├─ age: 58
├─ gender: Male
├─ requested_service: C5-C6 fusion
├─ symptoms: list
├─ imaging_findings: list
├─ failed_treatments: list
└─ documentation_notes: notes

Sheet: Complex_Case_Outcome
│
├─ criterion_name: Imaging Correlation
├─ description: Advanced imaging required
├─ met_status: MET
├─ evidence: MRI findings
└─ gap: (empty if MET)
```

---

## Validation Checklist

Before uploading your workbook, verify:

- [ ] All 6 sheets exist with correct names
- [ ] Training_Cases has at least 2 example PA cases
- [ ] Complex_Case_Input has all required fields populated
- [ ] Complex_Case_Outcome has approval criteria defined
- [ ] No empty cells in required columns
- [ ] Data types are appropriate (numbers, text, etc.)
- [ ] List items use consistent separators
- [ ] Sheet names are case-sensitive and exact

---

## Questions?

Contact support or review the QUICKSTART.md for more examples.
