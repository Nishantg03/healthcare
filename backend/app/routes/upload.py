from fastapi import APIRouter, File, UploadFile, HTTPException
import tempfile
import os
import shutil
from app.services.excel_parser import ExcelParser
from app.schemas.request_schema import UploadResponse

router = APIRouter()

# Global state for analysis - persists across requests
_current_file_path = None
_parser = None


@router.post("/upload", response_model=UploadResponse)
async def upload_workbook(file: UploadFile = File(...)):
    """Upload and parse healthcare pre-authorization workbook."""
    global _current_file_path, _parser
    
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="File must be .xlsx or .xls format")
    
    tmp_path = None
    persistent_path = None
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp.flush()  # Ensure data is written
            tmp_path = tmp.name
        
        # Parse workbook to validate
        parser = ExcelParser(tmp_path)
        parser.validate_workbook()
        cases = parser.get_all_cases()
        
        # Move to persistent location for analysis
        temp_dir = tempfile.gettempdir()
        persistent_path = os.path.join(temp_dir, "healthcare_copilot_current.xlsx")
        shutil.copy2(tmp_path, persistent_path)
        
        # Save global state for analyze endpoint
        _current_file_path = persistent_path
        _parser = ExcelParser(persistent_path)
        
        if not cases:
            return UploadResponse(
                cases=[],
                message="Workbook loaded but no PA cases found"
            )
        
        return UploadResponse(
            cases=cases,
            message=f"Successfully loaded {len(cases)} case(s) from workbook"
        )
    
    except Exception as e:
        # Clean up persistent file on error
        if persistent_path and os.path.exists(persistent_path):
            try:
                os.unlink(persistent_path)
            except:
                pass
        raise HTTPException(status_code=400, detail=f"Error processing workbook: {str(e)}")
    
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception as cleanup_err:
                print(f"Warning: Could not delete temp file: {cleanup_err}")
