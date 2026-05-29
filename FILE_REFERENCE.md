# File Structure & Purpose Reference

## 📋 Complete File Inventory

### Backend Files

#### Core Application
- **backend/app/main.py** - FastAPI application entry point
  - CORS configuration
  - Route registration
  - Health check endpoint

#### Routes (API Endpoints)
- **backend/app/routes/upload.py** - File upload endpoint
  - POST /upload - Parse and extract cases from workbook
  
- **backend/app/routes/analyze.py** - Analysis endpoints
  - POST /analyze - Analyze selected case
  - POST /analyze-inline - Analyze without stored workbook
  - POST /set-workbook - Store workbook for analysis

#### Services (Business Logic)
- **backend/app/services/excel_parser.py** - Workbook parsing
  - `ExcelParser` class - Parse Excel files
  - Sheet validation
  - Case extraction
  - Data schema reference loading

- **backend/app/services/normalization_service.py** - Data standardization
  - `NormalizationService` class - Normalize case data
  - Field extraction and mapping
  - List parsing (semicolon/comma separated)
  - LLM text formatting

- **backend/app/services/llm_service.py** - Groq API integration
  - `LLMService` class - Interface with Groq
  - Async API calls
  - Two-stage prompting (extraction + reasoning)
  - JSON response parsing

- **backend/app/services/reasoning_engine.py** - Pipeline orchestration
  - `ReasoningEngine` class - Orchestrate analysis
  - Stage 1: Extract clinical elements
  - Stage 2: Generate reasoning
  - Stage 3: Criteria matching
  - Stage 4: Confidence calculation

- **backend/app/services/criteria_matcher.py** - Rule-based evaluation
  - `CriteriaMatcher` class - Evaluate against criteria
  - Imaging severity assessment
  - Treatment failure evaluation
  - Functional impairment check
  - Medical necessity validation

- **backend/app/services/confidence_engine.py** - Confidence scoring
  - `ConfidenceEngine` class - Calculate confidence levels
  - Weighted scoring system
  - HIGH/MEDIUM/LOW classification

#### Schemas (Type Definitions)
- **backend/app/schemas/request_schema.py** - Request models
  - `AnalyzeRequest` - Case ID for analysis
  - `UploadResponse` - Response to upload

- **backend/app/schemas/response_schema.py** - Response models
  - `AnalysisResponse` - Complete analysis results
  - `CriterionResult` - Individual criterion evaluation
  - `NormalizedCase` - Standardized case data

#### Prompts (LLM Instructions)
- **backend/app/prompts/extraction_prompt.txt** - Stage 1 prompt
  - Instructions for LLM to extract clinical elements
  - Expected JSON output format
  - No hallucination constraints

- **backend/app/prompts/reasoning_prompt.txt** - Stage 2 prompt
  - Clinical reasoning instructions
  - Approval criteria evaluation
  - Recommendation generation
  - Provider question generation

#### Configuration Files
- **backend/requirements.txt** - Python dependencies
  - FastAPI, Uvicorn
  - Pandas, openpyxl
  - Pydantic, httpx
  - Groq SDK

- **backend/.env** - Environment variables (ACTIVE)
  - GROQ_API_KEY (Provided)
  - Backend configuration

- **backend/.env.example** - Environment template
  - Copy to .env and customize

- **backend/.gitignore** - Git ignore rules
  - Python cache files
  - Virtual environment
  - Environment variables
  - IDE files

- **backend/Dockerfile** - Docker image definition
  - Python 3.11 slim base
  - Dependency installation
  - Application setup
  - Port exposure

#### Package Files
- **backend/app/__init__.py** - Package initializer (empty)
- **backend/app/routes/__init__.py** - Routes package (empty)
- **backend/app/services/__init__.py** - Services package (empty)
- **backend/app/schemas/__init__.py** - Schemas package (empty)
- **backend/app/prompts/__init__.py** - Prompts package (empty)
- **backend/app/utils/__init__.py** - Utils package (empty)

---

### Frontend Files

#### App Router Pages
- **frontend/app/page.tsx** - Home page
  - Main entry point
  - Dynamic Dashboard import
  - Loading states

- **frontend/app/layout.tsx** - Root layout
  - HTML structure
  - Font configuration
  - Global metadata

- **frontend/app/globals.css** - Global styles
  - Tailwind directives
  - Scrollbar styling
  - Base styles

#### Components
- **frontend/components/Dashboard.tsx** - Main orchestrator (87 lines)
  - File upload handling
  - Case selection
  - Analysis workflow
  - Results display
  - State management
  - Error handling

- **frontend/components/UploadBox.tsx** - File upload (45 lines)
  - Drag-drop upload
  - File type validation
  - Loading states
  - Error/success messages

- **frontend/components/CaseSelector.tsx** - Case selection (48 lines)
  - Dropdown interface
  - Case list display
  - Selection handling
  - Loading state

- **frontend/components/RecommendationBadge.tsx** - Recommendation display (46 lines)
  - Color-coded recommendation
  - Confidence indicator
  - Progress bar
  - Icon display

- **frontend/components/SummaryCard.tsx** - Clinical summary (12 lines)
  - Summary text display
  - Styled card layout

- **frontend/components/CriteriaTable.tsx** - Criteria evaluation (72 lines)
  - Table structure
  - Status indicators
  - Evidence/gap display
  - Color coding

- **frontend/components/EvidenceList.tsx** - Supporting evidence (22 lines)
  - Evidence items
  - Checkmark icons
  - Empty state

- **frontend/components/MissingInfoCard.tsx** - Documentation gaps (29 lines)
  - Gap list
  - Warning styling
  - Empty state

- **frontend/components/ProviderQuestions.tsx** - Provider queries (31 lines)
  - Question display
  - Numbered format
  - Message icon

#### Services
- **frontend/services/api.ts** - API client (127 lines)
  - `ApiService` class
  - Axios configuration
  - All API methods
  - Type definitions (interfaces)
  - Error handling

#### Configuration Files
- **frontend/package.json** - Node dependencies
  - React 19, Next.js 15
  - TypeScript
  - Tailwind, Axios
  - Lucide React
  - Dev dependencies

- **frontend/tsconfig.json** - TypeScript configuration
  - Strict mode
  - Path aliases
  - Module resolution

- **frontend/next.config.ts** - Next.js configuration
  - TypeScript support
  - Experimental features
  - Optimization settings

- **frontend/tailwind.config.js** - Tailwind configuration
  - Color customization
  - Theme extensions

- **frontend/postcss.config.js** - PostCSS configuration
  - Autoprefixer
  - Tailwind processing

- **frontend/.env.local** - Environment variables (ACTIVE)
  - NEXT_PUBLIC_API_URL=http://localhost:8000

- **frontend/.env.example** - Environment template

- **frontend/.eslintrc.json** - ESLint configuration
  - Next.js rules

- **frontend/.gitignore** - Git ignore rules
  - Next.js build output
  - Node modules
  - Environment files

- **frontend/Dockerfile** - Docker image
  - Node 18 alpine base
  - Build optimization
  - Production start

---

### Documentation Files

- **README.md** (500+ lines)
  - Overview and features
  - Project structure
  - Setup instructions
  - API endpoints
  - Architecture overview
  - Troubleshooting

- **QUICKSTART.md** (200+ lines)
  - Quick setup guide
  - Environment variables
  - API endpoints reference
  - Common issues
  - Deployment guide

- **ARCHITECTURE.md** (800+ lines)
  - System overview
  - Architecture layers
  - Data flow diagrams
  - Two-stage reasoning
  - Criteria matching
  - Confidence calculation
  - Security considerations
  - File structure

- **DEPLOYMENT.md** (600+ lines)
  - Development vs production
  - Docker deployment
  - Cloud deployment options
  - Environment configuration
  - Performance optimization
  - Monitoring & logging
  - Database setup
  - CI/CD pipeline
  - Troubleshooting

- **EXCEL_WORKBOOK_GUIDE.md** (500+ lines)
  - Workbook structure
  - Sheet descriptions
  - Column requirements
  - Example data
  - Validation checklist

- **PROJECT_SUMMARY.md** (400+ lines)
  - Requirements fulfillment
  - Project structure
  - Feature summary
  - Getting started
  - Testing
  - Production readiness

---

### Utility Files

- **generate_sample_workbook.py** (200+ lines)
  - Generate sample Excel workbook
  - Creates all required sheets
  - Sample data
  - Styling with openpyxl

- **start.bat** (Windows startup script)
  - Python check
  - Node.js check
  - Virtual environment setup
  - Backend start (new window)
  - Frontend start (new window)
  - Service URLs display

- **start.sh** (Unix startup script)
  - Python check
  - Node.js check
  - Virtual environment setup
  - Backend start (background)
  - Frontend start (background)
  - Service URLs display
  - Cleanup on exit

---

### Configuration Files (Root)

- **docker-compose.yml** - Docker composition
  - Backend service
  - Frontend service
  - Volume configuration
  - Port mapping
  - Environment setup

- **.gitignore** - Git ignore rules (root)
  - All temporary files
  - IDE configurations
  - System files

---

## 📊 File Statistics

### Backend
- **Python Files**: 10+ files
- **Lines of Code**: ~1,500+ lines
- **Services**: 6 core services
- **Endpoints**: 3 main routes

### Frontend
- **TypeScript/TSX Files**: 10+ files
- **Components**: 8 components + Dashboard + API service
- **Lines of Code**: ~1,200+ lines
- **Pages**: 1 main page

### Documentation
- **Documentation Files**: 6 guides
- **Total Doc Lines**: 3,000+ lines
- **Code Examples**: 100+

### Configuration
- **Config Files**: 10+ files
- **Docker Files**: 3 files
- **Script Files**: 2 startup scripts
- **Generator**: 1 sample data script

---

## 🎯 File Organization Logic

### Backend Organization
```
Main Entry → Routes → Services → Schemas + Prompts
                ↓
         Business Logic Layer
                ↓
         Data Layer (Excel, LLM)
                ↓
         Response Layer
```

### Frontend Organization
```
Page → Dashboard Component → Child Components
           ↓
       API Service
           ↓
       Backend Routes
```

---

## 🔄 Data Flow Through Files

1. **Upload Flow**
   - `page.tsx` → `Dashboard.tsx` → `api.ts` → `upload.py` → `excel_parser.py`

2. **Analysis Flow**
   - `Dashboard.tsx` → `api.ts` → `analyze.py` → `reasoning_engine.py` → `llm_service.py`

3. **Rendering Flow**
   - Response → `Dashboard.tsx` → Child components (8 components)

---

## ✅ All Required Elements

- [x] Frontend: Next.js 15, React, TypeScript, Tailwind, Axios
- [x] Backend: FastAPI, Python, Pandas, Pydantic, openpyxl
- [x] LLM: Groq API integration
- [x] Two-stage reasoning: Extraction + Analysis
- [x] Deterministic criteria matching
- [x] Explainable recommendations
- [x] Professional dashboard UI
- [x] Comprehensive documentation
- [x] Docker support
- [x] Sample data generator
- [x] Startup scripts
- [x] Environment configuration
- [x] Error handling
- [x] Type safety throughout

---

## 🚀 Ready to Use

All files are in place and properly configured. Start with:
1. Review `QUICKSTART.md`
2. Run startup script (`start.bat` or `start.sh`)
3. Upload sample workbook
4. Test analysis
5. Review results

**Total Package**: 40+ files, 5,000+ lines of code, production-ready! 🎉
