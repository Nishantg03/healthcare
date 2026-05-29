from fastapi import APIRouter, HTTPException, UploadFile, File
import tempfile
import os
import json
from app.schemas.request_schema import AnalyzeRequest
from app.schemas.response_schema import AnalysisResponse
from app.services.excel_parser import ExcelParser
from app.services.llm_service import LLMService
from app.services.reasoning_engine import ReasoningEngine

router = APIRouter()

# Global references - lazy initialization
_llm_service = None
_reasoning_engine = None


def get_llm_service() -> LLMService:
    """Lazy initialize LLM service."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def get_reasoning_engine() -> ReasoningEngine:
    """Lazy initialize reasoning engine."""
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = ReasoningEngine(get_llm_service())
    return _reasoning_engine


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_case(request: AnalyzeRequest):
    """Analyze a selected pre-authorization case."""
    
    # Check for persisted workbook from upload
    temp_dir = tempfile.gettempdir()
    persistent_path = os.path.join(temp_dir, "healthcare_copilot_current.xlsx")
    
    if not os.path.exists(persistent_path):
        raise HTTPException(status_code=400, detail="No workbook loaded. Upload a workbook first.")
    
    try:
        # Initialize parser from persisted file
        parser = ExcelParser(persistent_path)
        
        # Extract case data (already normalized by parser)
        case_data = parser.get_case_data(request.case_id)
        
        if not case_data.get("case_input"):
            raise HTTPException(status_code=404, detail=f"Case {request.case_id} not found")
        
        # Get the normalized case input (already structured by parser)
        normalized_case_input = case_data["case_input"]
        
        # Convert to JSON string for LLM (clean structured JSON)
        normalized_case_json = json.dumps(normalized_case_input, indent=2)
        
        # Get training cases (for few-shot examples)
        training_cases_list = case_data.get("training_cases", [])
        training_text = json.dumps(training_cases_list[:3], indent=2) if training_cases_list else "[]"
        
        # Get approval criteria
        approval_criteria = case_data.get("approval_criteria", [])
        
        # Run analysis using the reasoning engine
        reasoning_engine = get_reasoning_engine()
        analysis_response = await reasoning_engine.analyze_case(
            case_id=request.case_id,
            normalized_case=normalized_case_json,
            training_cases=training_text,
            approval_criteria=approval_criteria
        )
        
        return analysis_response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Analyze endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error analyzing case: {str(e)}")


@router.post("/analyze-inline", response_model=AnalysisResponse)
async def analyze_case_inline(file: UploadFile = File(...), case_id: str = "COMPLEX_CASE"):
    """Analyze a case from an uploaded file without storing it."""
    
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="File must be .xlsx or .xls format")
    
    tmp_path = None
    try:
        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Parse and analyze
        parser = ExcelParser(tmp_path)
        parser.validate_workbook()
        
        raw_case_data = parser.get_case_data(case_id)
        if not raw_case_data.get("case_input"):
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
        # Normalize
        normalized_case = NormalizationService.normalize_case(raw_case_data)
        case_text = NormalizationService.format_for_llm(normalized_case)
        
        # Get training cases
        training_cases_list = raw_case_data.get("training_cases", [])
        training_text = "\n---\n".join([str(tc) for tc in training_cases_list[:3]])
        
        approval_criteria = raw_case_data.get("approval_criteria", [])
        
        # Analyze
        analysis_response = await _reasoning_engine.analyze_case(
            case_id=case_id,
            normalized_case=case_text,
            training_cases=training_text or "No training cases provided",
            approval_criteria=approval_criteria
        )
        
        return analysis_response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing case: {str(e)}")
    
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
