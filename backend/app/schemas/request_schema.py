from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    case_id: str


class UploadResponse(BaseModel):
    cases: list[str]
    message: str
