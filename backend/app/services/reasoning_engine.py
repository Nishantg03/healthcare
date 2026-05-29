from typing import Dict, Any, List
import json
from app.services.llm_service import LLMService
from app.services.criteria_matcher import CriteriaMatcher
from app.services.confidence_engine import ConfidenceEngine
from app.schemas.response_schema import AnalysisResponse, CriterionResult


class ReasoningEngine:
    """Orchestrate two-stage LLM reasoning and criteria matching."""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.criteria_matcher = CriteriaMatcher()
        self.confidence_engine = ConfidenceEngine()

    async def analyze_case(
        self,
        case_id: str,
        normalized_case: str,
        training_cases: str,
        approval_criteria: List[Dict[str, Any]]
    ) -> AnalysisResponse:
        """Execute two-stage reasoning pipeline."""
        
        try:
            print(f"[Stage 1] Extracting case data...")
            # Stage 1: Extract structured clinical data
            extraction = await self.llm.extract_case_data(normalized_case)
            print(f"[Stage 1] Extraction complete: {type(extraction)} - keys: {list(extraction.keys()) if isinstance(extraction, dict) else 'N/A'}")
        except Exception as e:
            print(f"[Stage 1] Error: {e}")
            extraction = {"symptoms": [], "imaging_findings": [], "failed_treatments": []}
        
        try:
            print(f"[Stage 2] Running analysis...")
            # Stage 2: Generate reasoning and recommendation
            criteria_str = self._format_criteria(approval_criteria)
            analysis = await self.llm.analyze_case(
                normalized_case,
                training_cases,
                criteria_str
            )
            print(f"[Stage 2] Analysis complete: {type(analysis)} - keys: {list(analysis.keys()) if isinstance(analysis, dict) else 'N/A'}")
        except Exception as e:
            error_msg = str(e)
            print(f"[Stage 2] Error: {error_msg}")
            
            # Provide meaningful clinical summary based on error
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                clinical_summary = "LLM service rate limited - evaluation based on available data only"
                print(f"[Stage 2] Detected rate limit: {error_msg[:200]}")
            elif "API" in error_msg or "Connection" in error_msg:
                clinical_summary = "LLM service unavailable - using rule-based evaluation"
                print(f"[Stage 2] Detected API error: {error_msg[:200]}")
            else:
                clinical_summary = f"Analysis error: {error_msg[:100]}"
                print(f"[Stage 2] Other error: {error_msg[:200]}")
            
            analysis = {
                "recommendation": "NEED_MORE_INFO",
                "clinical_summary": clinical_summary,
                "supporting_evidence": [],
                "missing_documentation": [],
                "provider_questions": [],
                "denial_risks": []
            }
        
        try:
            print(f"[Stage 3] Running criteria matching...")
            # Stage 3: Run deterministic criteria matching
            criteria_results = self.criteria_matcher.evaluate_criteria(
                case_input=normalized_case,
                extraction=extraction,
                approval_criteria=approval_criteria
            )
            print(f"[Stage 3] Criteria matching complete")
        except Exception as e:
            print(f"[Stage 3] Error: {e}")
            criteria_results = []
        
        try:
            print(f"[Stage 4] Calculating confidence...")
            # Stage 4: Calculate confidence
            confidence_level = self.confidence_engine.calculate_confidence(
                recommendation=analysis.get("recommendation", "NEED_MORE_INFO"),
                criteria_results=criteria_results,
                missing_docs=analysis.get("missing_documentation", []),
                supporting_evidence=analysis.get("supporting_evidence", [])
            )
            print(f"[Stage 4] Confidence: {confidence_level}")
        except Exception as e:
            print(f"[Stage 4] Error: {e}")
            confidence_level = "MEDIUM"
        
        # Build missing_information from LLM + criteria gaps for PARTIAL/NOT_MET
        missing_info = list(analysis.get("missing_documentation", []))
        for cr in criteria_results:
            if cr.status in ("PARTIAL", "NOT_MET") and cr.gap and cr.gap != "nan":
                # Add gap if not already present
                if cr.gap not in missing_info:
                    missing_info.append(cr.gap)
        
        # If LLM analysis failed, generate supporting evidence from MET criteria
        supporting_evidence = list(analysis.get("supporting_evidence", []))
        if len(supporting_evidence) == 0 and criteria_results:
            # Fallback: use MET criteria evidence as supporting evidence
            for cr in criteria_results:
                if cr.status == "MET" and cr.evidence and cr.evidence != "nan":
                    supporting_evidence.append(cr.evidence)
        
        # Build structured response
        response = AnalysisResponse(
            case_id=case_id,
            recommendation=analysis.get("recommendation", "NEED_MORE_INFO"),
            confidence=confidence_level,
            clinical_summary=analysis.get("clinical_summary", ""),
            criteria_results=criteria_results,
            supporting_evidence=supporting_evidence,
            missing_information=missing_info,
            provider_questions=analysis.get("provider_questions", []),
            denial_risks=analysis.get("denial_risks", [])
        )
        
        return response

    @staticmethod
    def _format_criteria(approval_criteria: List[Dict[str, Any]]) -> str:
        """Format approval criteria for LLM context."""
        if not approval_criteria:
            return "No specific criteria provided"
        
        formatted = "APPROVAL CRITERIA:\n"
        for idx, criterion in enumerate(approval_criteria, 1):
            if isinstance(criterion, dict):
                formatted += f"{idx}. {json.dumps(criterion, indent=2)}\n"
            else:
                formatted += f"{idx}. {str(criterion)}\n"
        
        return formatted
