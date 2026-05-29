# Healthcare Pre-Authorization Copilot

Production-grade AI-powered healthcare pre-authorization analysis and recommendation engine using Next.js 15, FastAPI, and Groq LLM.

## Overview

The Healthcare Pre-Authorization Copilot is an explainable AI system that analyzes healthcare pre-authorization patient cases from Excel workbooks and generates structured, auditable recommendations.

### Key Features

✅ **Excel Workbook Parsing** - Multi-sheet support for comprehensive case analysis
✅ **Explainable AI** - Two-stage LLM reasoning with deterministic criteria matching
✅ **Production Dashboard** - Professional UI for case analysis and recommendations
✅ **Audit Trail** - Complete reasoning and evidence tracking
✅ **Groq Integration** - Fast, efficient LLM processing
✅ **Type Safety** - Full TypeScript/Pydantic throughout

### Recommendation Types

- **LIKELY_APPROVE** - Strong evidence supports approval
- **LIKELY_DENY** - Significant gaps or contradictions
- **NEED_MORE_INFO** - Insufficient data for clear recommendation

## Project Structure

```
.
├── frontend/                 # Next.js 15 React application
│   ├── app/                 # App router structure
│   ├── components/          # React components
│   ├── services/            # API service layer
│   ├── package.json
│   └── tsconfig.json
│
└── backend/                 # FastAPI Python application
    ├── app/
    │   ├── routes/          # API endpoints
    │   ├── services/        # Business logic
    │   ├── schemas/         # Pydantic models
    │   ├── prompts/         # LLM prompts
    │   └── main.py         # FastAPI app
    ├── requirements.txt
    └── .env                # Environment variables
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
-- Groq API Key: `REPLACE_WITH_YOUR_GROQ_API_KEY`

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

![image alt](https://github.com/Nishantg03/healthcare/blob/0042434f63e529f5fc47896ec67cb0c5dbe46b6e/Screenshot%202026-05-29%20133610.png)

![image alt](https://github.com/Nishantg03/healthcare/blob/main/docs/media/screenshots/Screenshot%202026-05-29%20133639.png?raw=true)

![image alt](https://github.com/Nishantg03/healthcare/blob/main/docs/media/screenshots/Screenshot%202026-05-29%20133720.png?raw=true)

![image alt](https://github.com/Nishantg03/healthcare/blob/main/docs/media/screenshots/Screenshot%202026-05-29%20134851.png?raw=true)

![image alt](https://github.com/Nishantg03/healthcare/blob/main/docs/media/screenshots/Screenshot%202026-05-29%20134754.png?raw=true)

![image alt](https://github.com/Nishantg03/healthcare/blob/main/docs/media/screenshots/Screenshot%202026-05-29%20134744.png?raw=true)

https://github.com/Nishantg03/healthcare/tree/fe60e9be5a1d521b50f4d64e47be025d27c18db5/docs/media/videos

## Excel Workbook Format

Your Excel workbook must contain these sheets:

1. **Problem_Statement** - Ignored during processing
2. **Training_Cases** - PA cases used as reasoning examples
   - Columns: PA_ID, symptoms, imaging findings, failed treatments, documentation gaps, expected outcomes
3. **Patient_Data_Aspects** - Data category definitions (schema reference)
4. **Complex_Case_Input** - Patient case to analyze
5. **Complex_Case_Outcome** - Approval criteria and expected logic
6. **Suggested_Output** - Expected response structure

## API Endpoints

### Upload Workbook
```
POST /api/upload
Content-Type: multipart/form-data
Body: file (Excel workbook)

Response:
{
  "cases": ["PA-001", "PA-002", "COMPLEX_CASE"],
  "message": "Successfully loaded 3 case(s) from workbook"
}
```

### Analyze Case
```
POST /api/analyze
Content-Type: application/json
Body: {"case_id": "PA-001"}

Response:
{
  "case_id": "PA-001",
  "recommendation": "LIKELY_APPROVE|LIKELY_DENY|NEED_MORE_INFO",
  "confidence": "HIGH|MEDIUM|LOW",
  "clinical_summary": "...",
  "criteria_results": [...],
  "supporting_evidence": [...],
  "missing_information": [...],
  "provider_questions": [...],
  "denial_risks": [...]
}
```

### Inline Analysis
```
POST /api/analyze-inline?case_id=COMPLEX_CASE
Content-Type: multipart/form-data
Body: file (Excel workbook)

Response: Same as /analyze
```

## Architecture

### Backend Architecture

1. **Excel Parser** - Extracts and validates workbook structure
2. **Normalization Service** - Standardizes case data into structured JSON
3. **LLM Service** - Groq API integration
4. **Reasoning Engine** - Two-stage prompting orchestration:
   - Stage 1: Extract clinical elements
   - Stage 2: Generate reasoning & recommendation
5. **Criteria Matcher** - Deterministic rule-based logic
6. **Confidence Engine** - Calculates recommendation confidence

### Frontend Architecture

1. **API Service** - Axios-based backend communication
2. **Dashboard** - Main application interface
3. **Components**:
   - UploadBox - File upload with drag-drop
   - CaseSelector - Case selection dropdown
   - RecommendationBadge - Visual recommendation display
   - SummaryCard - Clinical summary
   - CriteriaTable - Criteria evaluation matrix
   - EvidenceList - Supporting evidence
   - MissingInfoCard - Documentation gaps
   - ProviderQuestions - Provider clarification questions

## LLM Reasoning Strategy

### Two-Stage Prompting

**Stage 1: Extraction**
- Extract symptoms, imaging findings, failed treatments, documentation gaps
- Return structured JSON with clinical elements

**Stage 2: Reasoning**
- Evaluate evidence against approval criteria
- Identify denial risks and missing documentation
- Generate explainable recommendation
- Calculate confidence level

### Deterministic Criteria Matching

Rule-based evaluation of:
- Imaging correlation severity
- Conservative treatment failure
- Functional impairment documentation
- Medical necessity

## Configuration

### Environment Variables

**Backend (.env)**
```
GROQ_API_KEY=your_api_key_here
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Performance Optimization

- **Efficient LLM**: Groq Mixtral 8x7b for fast inference
- **Async FastAPI**: Non-blocking request handling
- **Streaming Response**: Client-side loading states
- **Modular Services**: Reusable, testable components
- **Type Safety**: Full TypeScript/Pydantic reduces runtime errors

## Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Access at http://localhost:3000
```

### Production Deployment

1. **Backend**: Deploy FastAPI with Gunicorn/Uvicorn
2. **Frontend**: Build and deploy Next.js with Vercel/Netlify
3. **Environment**: Set production API URL
4. **Database**: Optional: Add PostgreSQL for case history
5. **Monitoring**: Set up logging and error tracking

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
pylint app/

# Frontend linting
npm run lint
```

## Troubleshooting

**Issue**: Workbook validation fails
- **Solution**: Ensure all required sheets exist and contain data

**Issue**: CORS errors
- **Solution**: Check backend CORS configuration in `main.py`

**Issue**: Groq API errors
- **Solution**: Verify API key in `.env` and Groq quota

**Issue**: LLM returns invalid JSON
- **Solution**: Check prompt formatting and temperature settings (currently set to 0.3)

## Security Considerations

- ✅ API key in environment variables (never in code)
- ✅ Input validation on all endpoints
- ✅ CORS properly configured
- ✅ File upload size limits recommended
- ✅ Type checking prevents injection attacks

## Future Enhancements

- 🚀 Case history database
- 🚀 Multi-user authentication
- 🚀 Batch case analysis
- 🚀 Provider feedback loop
- 🚀 Custom criteria templates
- 🚀 Denial appeal generation
- 🚀 Integration with EHR systems

## Support & Documentation

- API Documentation: http://localhost:8000/docs
- Component Library: See `frontend/components/`
- Service Layer: See `backend/app/services/`

## License

Proprietary - Healthcare Pre-Authorization Copilot

## Authors

Built with production-grade architecture for healthcare compliance.
