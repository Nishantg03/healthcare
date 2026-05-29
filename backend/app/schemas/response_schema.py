from pydantic import BaseModel
from typing import Optional


class CriterionResult(BaseModel):
    criterion: str
    status: str  # MET, PARTIAL, NOT_MET
    evidence: str
    gap: Optional[str] = None


class AnalysisResponse(BaseModel):
    case_id: str
    recommendation: str  # LIKELY_APPROVE, LIKELY_DENY, NEED_MORE_INFO
    confidence: str  # HIGH, MEDIUM, LOW
    clinical_summary: str
    criteria_results: list[CriterionResult]
    supporting_evidence: list[str]
    missing_information: list[str]
    provider_questions: list[str]
    denial_risks: Optional[list[str]] = None

    @property
    def confidence_level(self) -> str:
        """Backward-compatible alias for `confidence` used in older tests."""
        return self.confidence


class NormalizedCase(BaseModel):
    case_id: str
    patient: dict
    requested_service: str
    symptoms: list[str]
    imaging_findings: list[str]
    failed_treatments: list[str]
    documentation_notes: list[str]
    additional_context: Optional[dict] = None
