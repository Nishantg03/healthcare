from typing import List, Dict, Any
from app.schemas.response_schema import CriterionResult


class ConfidenceEngine:
    """Calculate confidence level based on evidence completeness and criteria."""

    def calculate_confidence(
        self,
        recommendation: str,
        criteria_results: List[CriterionResult],
        missing_docs: List[str],
        supporting_evidence: List[str]
    ) -> str:
        """Calculate confidence level: HIGH, MEDIUM, or LOW."""
        
        score = 0
        max_score = 100
        
        # Evaluate criteria status (40% weight)
        criteria_score = self._evaluate_criteria(criteria_results)
        score += criteria_score * 0.4
        
        # Evaluate evidence completeness (30% weight)
        evidence_score = self._evaluate_evidence(supporting_evidence, missing_docs)
        score += evidence_score * 0.3
        
        # Evaluate documentation gaps (20% weight)
        doc_score = self._evaluate_documentation(missing_docs)
        score += doc_score * 0.2
        
        # Recommendation consistency (10% weight)
        consistency_score = self._evaluate_consistency(recommendation, criteria_results)
        score += consistency_score * 0.1
        
        # Convert score to confidence level
        if score >= 75:
            return "HIGH"
        elif score >= 50:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def _evaluate_criteria(criteria_results: List[CriterionResult]) -> int:
        """Score based on criteria met/partial/not met."""
        if not criteria_results:
            return 0
        
        met_count = sum(1 for c in criteria_results if c.status == "MET")
        partial_count = sum(1 for c in criteria_results if c.status == "PARTIAL")
        not_met_count = sum(1 for c in criteria_results if c.status == "NOT_MET")
        
        total = len(criteria_results)
        score = (met_count * 100 + partial_count * 50 + not_met_count * 0) / (total * 100)
        return int(score * 100)

    @staticmethod
    def _evaluate_evidence(supporting_evidence: List[str], missing_docs: List[str]) -> int:
        """Score based on evidence quantity and gaps."""
        evidence_count = len(supporting_evidence)
        gap_count = len(missing_docs)
        
        # Ideal: 5+ pieces of evidence, 0-2 gaps
        if evidence_count >= 5 and gap_count <= 2:
            return 100
        elif evidence_count >= 3 and gap_count <= 2:
            return 75
        elif evidence_count >= 2 or gap_count >= 3:
            return 50
        else:
            return 25

    @staticmethod
    def _evaluate_documentation(missing_docs: List[str]) -> int:
        """Score based on missing documentation."""
        gap_count = len(missing_docs)
        
        if gap_count == 0:
            return 100
        elif gap_count <= 2:
            return 75
        elif gap_count <= 4:
            return 50
        else:
            return 25

    @staticmethod
    def _evaluate_consistency(recommendation: str, criteria_results: List[CriterionResult]) -> int:
        """Score recommendation consistency with criteria."""
        met_count = sum(1 for c in criteria_results if c.status == "MET")
        total_count = len(criteria_results)
        
        if total_count == 0:
            return 50
        
        met_percentage = (met_count / total_count) * 100
        
        # Check consistency
        if recommendation == "LIKELY_APPROVE" and met_percentage >= 70:
            return 100
        elif recommendation == "LIKELY_DENY" and met_percentage <= 30:
            return 100
        elif recommendation == "NEED_MORE_INFO" and 30 < met_percentage < 70:
            return 100
        else:
            return 50
