# LLM Implementation & Flow Guide

## 1. INITIALIZATION FLOW

```
Backend Starts
    ↓
main.py includes analyze.py router
    ↓
ReasoningEngine imported (lazy-initialized on first /analyze request)
    ↓
LLMService.__init__() called
    ├─ Load GROQ_API_KEY from backend/.env
    ├─ Load GROQ_MODEL from backend/.env (or auto-detect via /models endpoint)
    └─ Initialize httpx.AsyncClient
```

### Key Files:
- **backend/.env** - Must have: GROQ_API_KEY=gsk_... and GROQ_MODEL=groq/compound-mini
- **backend/app/services/llm_service.py** - LLM initialization & API calls
- **backend/app/routes/analyze.py** - HTTP endpoint that triggers LLM

---

## 2. TWO-STAGE PIPELINE

### STAGE 1: Case Data Extraction (Optional LLM)
```
User clicks "Analyze" in UI
    ↓
POST /api/analyze with case_id="PA-001"
    ↓
ReasoningEngine.analyze_case() starts
    ↓
[STAGE 1] LLMService.extract_case_data()
    ├─ Read prompt: backend/app/prompts/extraction_prompt.txt
    ├─ Substitute {case_data} with JSON case input
    ├─ POST to Groq API /chat/completions
    └─ Parse response JSON
         ├─ If SUCCESS: Returns {symptoms[], imaging_findings[], failed_treatments[], ...}
         └─ If FAILS (rate limit 429, auth error 401, etc):
              └─ FALLBACK: Return empty dict {}
```

### STAGE 2: Clinical Analysis & Recommendation (Optional LLM)
```
[STAGE 2] LLMService.analyze_case()
    ├─ Read prompt: backend/app/prompts/reasoning_prompt.txt
    ├─ Substitute {case_data}, {training_cases}, {approval_criteria}
    ├─ POST to Groq API /chat/completions
    └─ Parse response JSON
         ├─ If SUCCESS: Returns {recommendation, clinical_summary, supporting_evidence[], missing_documentation[], ...}
         └─ If FAILS (rate limit 429, auth error 401, etc):
              └─ FALLBACK: Return {recommendation: "NEED_MORE_INFO", clinical_summary: "Analysis error", ...}
```

### STAGE 3: Deterministic Criteria Matching (NO LLM)
```
[STAGE 3] CriteriaMatcher.evaluate_criteria()
    ├─ Merge LLM extraction + parser case_input data (fallback to parser if LLM failed)
    ├─ Evaluate 6 criteria using rule-based logic
    └─ Return criteria_results[] with status (MET/PARTIAL/NOT_MET)
         └─ Now: Uses parser data if LLM extraction empty ✓ (FIXED)
```

### STAGE 4: Confidence Calculation (NO LLM)
```
[STAGE 4] ConfidenceEngine.calculate_confidence()
    ├─ Input: recommendation, criteria_results[], supporting_evidence[], missing_docs[]
    └─ Output: confidence level (HIGH/MEDIUM/LOW)
```

---

## 3. WHERE ISSUES CAN OCCUR

### Issue #1: API Key Not Loaded
```
Symptom: ValueError("GROQ_API_KEY environment variable not set")
Root Cause: backend/.env missing or GROQ_API_KEY not set
Fix:
  1. Check: backend/.env exists
  2. Check: backend/.env has GROQ_API_KEY=gsk_...
  3. Restart backend: python -m uvicorn app.main:app --reload
```

### Issue #2: Model Not Found
```
Symptom: "Model not found" or 404 error from Groq API
Root Cause: GROQ_MODEL env var has old/decommissioned model
Flow:
  1. LLMService auto-detects available models from /models endpoint
  2. Preferred: mixtral-8x7b-32768
  3. Fallback: Any mixtral model, then GROQ_MODEL env var
Fix:
  1. Set GROQ_MODEL=groq/compound-mini in backend/.env
  2. Or leave blank to auto-detect (recommended)
```

### Issue #3: Rate Limit Exceeded (429)
```
Symptom: "Rate limit reached for model..." after ~100K tokens used
Root Cause: Groq API tier limits tokens per minute
Behavior:
  - STAGE 1 (Extraction): May succeed (uses ~500 tokens)
  - STAGE 2 (Analysis): Often fails (uses ~2000 tokens, pushes over limit)
  - Response: {"error": {"code": "rate_limit_exceeded", ...}}
  - Handler: Exception caught → STAGE 2 returns fallback analysis
Result: Recommendation="NEED_MORE_INFO", confidence=LOW, clinical_summary="Analysis error"

Fix: 
  1. Wait 15-60 seconds before re-running analysis
  2. Upgrade Groq tier at https://console.groq.com/settings/billing
  3. Implement mock LLM mode (env GROQ_USE_MOCK=1)
```

### Issue #4: JSON Parsing Failures
```
Symptom: LLM response returned but not valid JSON
Root Cause: LLM returns markdown code block or invalid JSON
Handler: _parse_json_response() tries multiple strategies:
  1. Direct JSON parse
  2. Extract from ```json ... ``` block
  3. Extract from ``` ... ``` block
  4. Regex search for { ... }
  5. If all fail: Return empty dict {}
Result: Criteria still evaluate (Stage 3), but missing LLM insights
```

---

## 4. STEP-BY-STEP DEBUGGING

### Step 1: Check Environment Setup
```bash
cd "c:\Users\nisha\OneDrive\Desktop\health care 1"
python -c "import os; print(f'GROQ_API_KEY: {os.getenv(\"GROQ_API_KEY\")[:20]}...'); print(f'GROQ_MODEL: {os.getenv(\"GROQ_MODEL\")}')"
```

Expected output:
```
GROQ_API_KEY: gsk_...
GROQ_MODEL: groq/compound-mini
```

### Step 2: Test LLMService Directly
```bash
python << 'EOF'
import asyncio, sys
sys.path.insert(0, 'backend')
from app.services.llm_service import llm_service

async def test():
    llm = LLMService()
    print(f"Model: {llm.model}")
    print(f"API Key: {llm.api_key[:20]}...")
    
    # Test extraction
    test_case = '{"symptoms": ["pain"], "imaging": ["MRI shows stenosis"]}'
    result = await llm.extract_case_data(test_case)
    print(f"Extraction result: {result}")

asyncio.run(test())
EOF
```

### Step 3: Test Full Pipeline with Diagnostics
```bash
python test_pipeline_fixed.py
```

Look for these markers in output:
```
[Stage 1] Extraction complete: <class 'dict'> - keys: [...]  ✓ Succeeded
[Stage 2] Analysis complete: <class 'dict'> - keys: [...]   ✓ Succeeded
[Stage 2] Error: Groq API error: ... 429 ...                ✗ Rate limit hit
[Stage 3] Criteria matching complete                        ✓ Always succeeds
[Stage 4] Confidence: MEDIUM                                ✓ Always succeeds
```

### Step 4: Check API Response
```bash
python test_api.py
```

Expected:
```
Criteria (4 items):
  Imaging Correlation: MET  ✓
  Conservative Treatment Failure: MET  ✓
  Functional Impairment: PARTIAL or MET  ✓
  Medical Necessity: MET  ✓

Supporting Evidence (4+ items):  ✓ (empty if LLM failed)
Missing Information (2+ items): ✓ (shows gaps from PARTIAL criteria)
```

### Step 5: Check Backend Logs
```
Backend terminal should show:
  [Stage 1] Extracting case data...
  [Stage 1] Extraction complete
  [Stage 2] Running analysis...
  [Stage 2] Analysis complete (or Error: ...)
  [Stage 3] Running criteria matching...
  [Stage 4] Calculating confidence...
```

---

## 5. COMMON ISSUES & SOLUTIONS

| Issue | Symptom | Fix |
|-------|---------|-----|
| **API Key Missing** | ValueError on startup | Add `GROQ_API_KEY=...` to backend/.env |
| **Model Decommissioned** | 404 or model not found | Update `GROQ_MODEL=groq/compound-mini` |
| **Rate Limit (429)** | Stage 2 fails, shows "Analysis error" | Wait 15s or upgrade Groq tier |
| **JSON Parse Error** | LLM response not valid JSON | Check backend logs for [DEBUG] messages |
| **All Criteria NOT_MET** | BEFORE: Criteria matcher saw empty extraction (FIXED ✓) | Matcher now merges parser data |
| **Missing Information Empty** | BEFORE: Criteria gaps not shown (FIXED ✓) | Engine now merges criteria gaps |

---

## 6. ARCHITECTURE SUMMARY

```
┌──────────────────────────────────────────────┐
│         Frontend (React)                     │
│   Upload → /api/upload (file)                │
│   Analyze → /api/analyze (case_id: PA-001)   │
└────────────────┬─────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────┐
│    Backend (FastAPI + Python)                │
│                                              │
│  ExcelParser                                 │
│    ├─ Parse case_input (normalized JSON)     │
│    ├─ Parse approval_criteria                │
│    └─ Parse training_cases                   │
│         ↓                                    │
│  ReasoningEngine (orchestrator)              │
│    ├─ Stage 1: LLMService.extract_case()    │
│    ├─ Stage 2: LLMService.analyze_case()    │
│    ├─ Stage 3: CriteriaMatcher (rule-based) │
│    └─ Stage 4: ConfidenceEngine              │
│         ↓                                    │
│  AnalysisResponse (JSON)                     │
│    ├─ recommendation                        │
│    ├─ confidence                            │
│    ├─ criteria_results[]                    │
│    ├─ supporting_evidence[]                 │
│    ├─ missing_information[]                 │
│    └─ clinical_summary                      │
└────────────────┬─────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────┐
│      Groq LLM API (Optional)                 │
│   Stage 1: Extract data (~500 tokens)        │
│   Stage 2: Generate analysis (~2000 tokens)  │
│                                              │
│   Rate Limit: ~100K tokens/day free tier     │
│   Error 429: Rate limit exceeded             │
│   Error 401: Invalid API key                 │
│   Error 404: Model not found                 │
└──────────────────────────────────────────────┘
```

---

## 7. WHAT'S BEEN FIXED ✓

✅ **JSON Parsing in Prompts** - Changed `.format()` to `.replace()` to avoid brace conflicts with JSON
✅ **Model Auto-Detection** - Queries `/models` endpoint to find available model
✅ **Environment Loading** - dotenv.load_dotenv() at module import so tests pick up .env
✅ **Criteria Matcher Merge** - Now merges LLM extraction + parser case_input (fallback to parser)
✅ **Missing Information Sync** - Now includes criteria gaps when LLM fails

---

## 8. NEXT TROUBLESHOOTING STEPS

If you still see issues:

1. **Restart Backend**:
   ```bash
   # Kill old process
   taskkill /PID <pid> /F
   # Restart
   cd backend && python -m uvicorn app.main:app --reload
   ```

2. **Check .env is Loaded**:
   ```bash
   python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GROQ_MODEL'))"
   ```

3. **Run Diagnostics**:
   ```bash
   python diagnostic_case_data.py
   python diagnostic_criteria.py
   python diagnostic_matcher.py
   ```

4. **Check API Live**:
   ```bash
   curl http://localhost:8000/api/analyze -X POST -H "Content-Type: application/json" -d "{\"case_id\":\"PA-001\"}"
   ```

5. **Enable Mock Mode** (to bypass LLM completely):
   - Add `GROQ_USE_MOCK=1` to backend/.env
   - Backend will use mock responses instead of Groq API
