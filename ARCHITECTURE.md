# Architecture Documentation

## System Overview

Healthcare Pre-Authorization Copilot is a production-grade, full-stack AI system designed for explainable medical pre-authorization analysis.

### Technology Stack

```
Frontend:
├── Next.js 15 (App Router)
├── React 19
├── TypeScript
├── Tailwind CSS
├── Axios
└── Lucide React Icons

Backend:
├── FastAPI
├── Python 3.10+
├── Pydantic (Type validation)
├── Pandas (Data processing)
├── openpyxl (Excel parsing)
└── Groq API (LLM inference)
```

---

## Architecture Layers

### 1. Frontend Architecture

```
┌─────────────────────────────────────────────┐
│            User Interface (React)            │
├─────────────────────────────────────────────┤
│  Components Layer                           │
│  ├── UploadBox (File upload with drag-drop)│
│  ├── CaseSelector (Case selection)          │
│  ├── RecommendationBadge (Visual display)  │
│  ├── CriteriaTable (Criteria evaluation)   │
│  ├── EvidenceList (Supporting evidence)    │
│  ├── MissingInfoCard (Documentation gaps)  │
│  ├── ProviderQuestions (Provider queries)  │
│  └── Dashboard (Main orchestrator)         │
├─────────────────────────────────────────────┤
│  API Service Layer (Axios)                 │
│  ├── uploadWorkbook()                      │
│  ├── analyzeCase()                         │
│  ├── analyzeCaseInline()                   │
│  └── healthCheck()                         │
├─────────────────────────────────────────────┤
│  Backend API (FastAPI, :8000)              │
└─────────────────────────────────────────────┘
```

### 2. Backend Architecture

```
┌─────────────────────────────────────────────────┐
│            FastAPI Application                  │
├─────────────────────────────────────────────────┤
│  Routes Layer (HTTP Endpoints)                 │
│  ├── POST /upload                              │
│  ├── POST /analyze                             │
│  └── POST /analyze-inline                      │
├─────────────────────────────────────────────────┤
│  Services Layer (Business Logic)               │
│  ├── ExcelParser                               │
│  │   ├── validate_workbook()                  │
│  │   ├── get_all_cases()                      │
│  │   └── get_case_data()                      │
│  │                                             │
│  ├── NormalizationService                      │
│  │   ├── normalize_case()                     │
│  │   ├── format_for_llm()                     │
│  │   └── extract_list()                       │
│  │                                             │
│  ├── LLMService (Groq Integration)            │
│  │   ├── extract_case_data()                  │
│  │   ├── analyze_case()                       │
│  │   └── _call_groq()                         │
│  │                                             │
│  ├── ReasoningEngine (Orchestrator)           │
│  │   ├── Stage 1: Extraction                  │
│  │   ├── Stage 2: Reasoning                   │
│  │   ├── Stage 3: Criteria Matching           │
│  │   └── Stage 4: Confidence Calculation      │
│  │                                             │
│  ├── CriteriaMatcher (Rule-based)             │
│  │   ├── Imaging severity assessment          │
│  │   ├── Treatment history validation         │
│  │   ├── Functional impairment check          │
│  │   └── Medical necessity evaluation         │
│  │                                             │
│  └── ConfidenceEngine                          │
│      ├── Criteria evaluation (40%)             │
│      ├── Evidence completeness (30%)           │
│      ├── Documentation gaps (20%)              │
│      └── Recommendation consistency (10%)      │
│                                                 │
├─────────────────────────────────────────────────┤
│  Schemas Layer (Type Validation - Pydantic)   │
│  ├── AnalyzeRequest                            │
│  ├── AnalysisResponse                          │
│  ├── NormalizedCase                            │
│  ├── CriterionResult                           │
│  └── UploadResponse                            │
│                                                 │
├─────────────────────────────────────────────────┤
│  Prompts (LLM Instructions)                   │
│  ├── extraction_prompt.txt (Stage 1)          │
│  └── reasoning_prompt.txt (Stage 2)           │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Data Flow

### Upload & Parsing Flow

```
1. User uploads Excel workbook (.xlsx)
   ↓
2. UploadBox component validates file type
   ↓
3. API request: POST /upload
   ↓
4. FastAPI receives file
   ↓
5. ExcelParser validates required sheets
   ↓
6. Extract PA case IDs from workbooks
   ↓
7. Return list of cases to frontend
   ↓
8. CaseSelector displays available cases
```

### Analysis Flow

```
1. User selects case and clicks "Analyze"
   ↓
2. API request: POST /analyze {case_id}
   ↓
3. ExcelParser extracts case data
   ↓
4. NormalizationService standardizes format
   ↓
5. ReasoningEngine orchestrates analysis:
   │
   ├─ Stage 1: LLMService.extract_case_data()
   │  ├─ Uses extraction_prompt.txt
   │  ├─ Groq API call (fast inference)
   │  └─ Returns structured clinical elements
   │
   ├─ Stage 2: LLMService.analyze_case()
   │  ├─ Uses reasoning_prompt.txt with examples
   │  ├─ Groq API call with few-shot context
   │  └─ Returns recommendation & reasoning
   │
   ├─ Stage 3: CriteriaMatcher.evaluate_criteria()
   │  ├─ Deterministic rule-based evaluation
   │  ├─ MET / PARTIAL / NOT_MET status
   │  └─ Evidence & gap identification
   │
   └─ Stage 4: ConfidenceEngine.calculate_confidence()
      ├─ Weighted scoring (40/30/20/10)
      └─ HIGH / MEDIUM / LOW confidence
   ↓
6. Build AnalysisResponse with all results
   ↓
7. Return JSON to frontend
   ↓
8. Dashboard displays results with:
   ├─ RecommendationBadge
   ├─ SummaryCard
   ├─ CriteriaTable
   ├─ EvidenceList
   ├─ MissingInfoCard
   └─ ProviderQuestions
```

---

## Two-Stage LLM Reasoning

### Stage 1: Extraction

**Purpose:** Extract structured clinical elements from unstructured case text

**Input:**
- Raw case data from Excel
- Extraction template

**Processing:**
```
Extraction Prompt Template:
├─ Extract symptoms
├─ Extract imaging findings
├─ Extract failed treatments
├─ Extract neurologic deficits
└─ Identify documentation gaps

LLM Output Format:
{
  "symptoms": [...],
  "imaging_findings": [...],
  "failed_treatments": [...],
  "neurologic_deficits": [...],
  "documentation_gaps": [...]
}
```

**Output:** Structured JSON with clinical elements

### Stage 2: Reasoning

**Purpose:** Generate explainable recommendation based on criteria and examples

**Input:**
- Normalized case data
- Training cases (few-shot examples)
- Approval criteria
- Stage 1 extraction results

**Processing:**
```
Reasoning Prompt Template:
├─ Present training cases as reasoning examples
├─ Provide approval criteria to evaluate
├─ Request evidence extraction
├─ Request denial risk identification
├─ Request missing documentation identification
└─ Request recommendation with confidence

LLM Output Format:
{
  "clinical_summary": "...",
  "supporting_evidence": [...],
  "denial_risks": [...],
  "missing_documentation": [...],
  "recommendation": "LIKELY_APPROVE|DENY|NEED_MORE_INFO",
  "confidence": "HIGH|MEDIUM|LOW",
  "provider_questions": [...],
  "reasoning": "..."
}
```

**Output:** Explainable recommendation with supporting analysis

---

## Criteria Matching Engine

### Deterministic Rule-Based Logic

The system implements hard-coded evaluation rules:

```python
IMAGING_CORRELATION:
├─ if severe_keywords_count >= 2: MET
├─ elif moderate_keywords_count >= 1: PARTIAL
└─ else: NOT_MET

CONSERVATIVE_TREATMENT:
├─ if failed_treatments_count >= 2: MET
├─ elif failed_treatments_count == 1: PARTIAL
└─ else: NOT_MET

FUNCTIONAL_IMPAIRMENT:
├─ if symptoms + no_doc_gaps: MET
├─ elif symptoms OR doc_gaps: PARTIAL
└─ else: NOT_MET

MEDICAL_NECESSITY:
├─ if requested_service AND (symptoms OR imaging): MET
└─ else: PARTIAL
```

---

## Confidence Calculation

### Weighted Scoring System

```
Final Confidence Score = 
  (Criteria_Score × 0.40) +
  (Evidence_Score × 0.30) +
  (Documentation_Score × 0.20) +
  (Consistency_Score × 0.10)

Criteria_Score:
├─ MET criteria: 100 points each
├─ PARTIAL criteria: 50 points each
└─ NOT_MET criteria: 0 points each

Evidence_Score:
├─ 5+ pieces: 100
├─ 3-4 pieces: 75
├─ 2 pieces: 50
└─ <2 pieces: 25

Documentation_Score:
├─ 0 gaps: 100
├─ 1-2 gaps: 75
├─ 3-4 gaps: 50
└─ 5+ gaps: 25

Consistency_Score:
├─ Recommendation aligns with criteria: 100
└─ Misalignment detected: 50

Confidence Level:
├─ Score >= 75: HIGH
├─ Score >= 50: MEDIUM
└─ Score < 50: LOW
```

---

## Error Handling & Validation

### Input Validation

```
Excel Upload:
├─ File type check (.xlsx, .xls)
├─ Required sheets validation
├─ Data type validation (Pydantic)
└─ Empty field detection

Case Extraction:
├─ PA_ID existence check
├─ Data completeness check
├─ Type consistency validation
└─ Fallback to defaults

LLM Integration:
├─ API key validation
├─ Response format validation
├─ JSON parsing with fallback
└─ Timeout handling
```

---

## Performance Optimization

### Backend Optimizations

1. **Async FastAPI Routes**
   - Non-blocking I/O operations
   - Concurrent request handling
   - Proper use of `async/await`

2. **Efficient LLM Usage**
   - Groq Mixtral 8x7b (fast, efficient)
   - Low temperature (0.3) for consistent output
   - Streaming response support
   - Caching of training examples

3. **Smart Data Processing**
   - Lazy loading of Excel sheets
   - In-memory case caching
   - Minimal data duplication

### Frontend Optimizations

1. **Next.js 15 Features**
   - Server-side rendering where beneficial
   - Dynamic imports for components
   - Optimized image loading
   - CSS-in-JS with Tailwind

2. **React Performance**
   - Component memoization
   - Event handler optimization
   - Efficient state management
   - Lazy loading of heavy components

---

## Security Considerations

### 1. API Security

```
✅ CORS Properly Configured
├─ Limited to localhost:3000 for dev
├─ Configurable for production
└─ Credentials supported

✅ Input Validation
├─ Pydantic type checking
├─ File size limits (implement)
├─ Rate limiting (implement)
└─ SQL injection prevention (N/A - no DB)

✅ Error Messages
├─ Generic messages in production
├─ Detailed logs server-side
└─ No sensitive data leakage
```

### 2. Environment Variables

```
✅ Secrets Management
├─ GROQ_API_KEY in .env (never committed)
├─ Backend configuration in .env
├─ Frontend config in .env.local
└─ .gitignore protects sensitive files
```

### 3. Data Privacy

```
✅ Case Data Handling
├─ Temporary file cleanup
├─ No persistent storage (current)
├─ HIPAA considerations for production
└─ Audit logging (recommended)
```

---

## Scalability Considerations

### Current Architecture

- Single backend instance
- Single frontend instance
- In-memory case storage
- Synchronous database calls (none currently)

### Production Scaling

```
Frontend Scaling:
├─ Deploy with Vercel/Netlify
├─ CDN for static assets
└─ Multi-region deployment

Backend Scaling:
├─ Horizontal scaling with load balancer
├─ Stateless service design
├─ Database for case history
├─ Redis for session caching
├─ Message queue for async jobs
└─ Groq API for LLM inference

Database Considerations:
├─ PostgreSQL for case history
├─ Redis for caching
└─ S3 for Excel file storage
```

---

## Monitoring & Logging

### Recommended Additions

```
Application Monitoring:
├─ Sentry for error tracking
├─ Datadog for performance metrics
└─ CloudWatch for cloud deployment

Logging Strategy:
├─ Request/response logging
├─ LLM API call logging
├─ Error stack traces
├─ Analysis audit trail
└─ User action tracking
```

---

## File Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app initialization
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── upload.py        # Upload endpoint
│   │   │   ├── analyze.py       # Analysis endpoint
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── excel_parser.py           # Workbook parsing
│   │   │   ├── normalization_service.py  # Data normalization
│   │   │   ├── llm_service.py            # Groq integration
│   │   │   ├── reasoning_engine.py       # Analysis orchestration
│   │   │   ├── criteria_matcher.py       # Rule-based evaluation
│   │   │   ├── confidence_engine.py      # Confidence scoring
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── request_schema.py         # Request models
│   │   │   ├── response_schema.py        # Response models
│   │   │   └── __init__.py
│   │   ├── prompts/
│   │   │   ├── extraction_prompt.txt     # Stage 1 prompt
│   │   │   ├── reasoning_prompt.txt      # Stage 2 prompt
│   │   │   └── __init__.py
│   │   ├── utils/
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── .env
│   ├── .gitignore
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main page
│   │   ├── layout.tsx           # Root layout
│   │   ├── globals.css          # Global styles
│   │   └── dashboard/           # Dashboard routes
│   ├── components/
│   │   ├── Dashboard.tsx        # Main component
│   │   ├── UploadBox.tsx        # File upload
│   │   ├── CaseSelector.tsx     # Case selection
│   │   ├── RecommendationBadge.tsx
│   │   ├── SummaryCard.tsx
│   │   ├── CriteriaTable.tsx
│   │   ├── EvidenceList.tsx
│   │   ├── MissingInfoCard.tsx
│   │   └── ProviderQuestions.tsx
│   ├── services/
│   │   └── api.ts               # API service
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── tailwind.config.js
│   ├── .env.local
│   ├── .eslintrc.json
│   ├── .gitignore
│   └── Dockerfile
│
├── README.md
├── QUICKSTART.md
├── EXCEL_WORKBOOK_GUIDE.md
├── docker-compose.yml
├── start.bat                    # Windows startup
├── start.sh                     # Unix startup
└── generate_sample_workbook.py  # Sample data generator
```

---

## API Response Examples

### Upload Response

```json
{
  "cases": ["PA-001", "PA-002", "COMPLEX_CASE"],
  "message": "Successfully loaded 3 case(s) from workbook"
}
```

### Analysis Response

```json
{
  "case_id": "PA-001",
  "recommendation": "LIKELY_APPROVE",
  "confidence": "HIGH",
  "clinical_summary": "58-year-old male with progressive cervical myelopathy and clear imaging evidence of severe stenosis with cord compression. Multiple failed conservative treatments documented. Significant functional impairment noted.",
  "criteria_results": [
    {
      "criterion": "Imaging Correlation",
      "status": "MET",
      "evidence": "MRI severe stenosis, cord compression",
      "gap": null
    },
    {
      "criterion": "Conservative Treatment Failure",
      "status": "MET",
      "evidence": "PT, NSAIDs, gabapentin, epidural injection",
      "gap": null
    },
    {
      "criterion": "Functional Impairment",
      "status": "PARTIAL",
      "evidence": "Difficulty grooming, eating",
      "gap": "Explicit ADL wording could be clearer"
    }
  ],
  "supporting_evidence": [
    "Cord compression on MRI",
    "Failed physical therapy",
    "Hyperreflexia on exam"
  ],
  "missing_information": [
    "Formal functional assessment score"
  ],
  "provider_questions": [
    "Can you provide formal ADL assessment?"
  ],
  "denial_risks": [
    "Documentation of ADL could be more explicit"
  ]
}
```

---

## Future Enhancements

1. **Database Integration** - Persistent case history and audit logs
2. **User Authentication** - Multi-user support with role-based access
3. **Batch Processing** - Analyze multiple cases at once
4. **Custom Criteria** - Allow clients to define criteria templates
5. **Provider Feedback** - Collect feedback on recommendations for model improvement
6. **EHR Integration** - Direct import from healthcare systems
7. **Appeal Generation** - Generate structured denial appeals
8. **Mobile App** - React Native mobile interface
9. **Advanced Analytics** - Recommendation accuracy tracking
10. **Custom LLM** - Fine-tuned models for specific specialties
