import json
from typing import Dict, Any, List
from app.schemas.response_schema import CriterionResult


class CriteriaMatcher:
    """Deterministic rule-based criteria matching engine."""

    def evaluate_criteria(
        self,
        case_input: str,
        extraction: Dict[str, Any],
        approval_criteria: List[Dict[str, Any]]
    ) -> List[CriterionResult]:
        """Evaluate case against approval criteria."""
        
        results = []
        
        # Parse case_input JSON if needed
        if isinstance(case_input, str):
            try:
                case_input_dict = json.loads(case_input)
            except (json.JSONDecodeError, TypeError):
                case_input_dict = {}
        else:
            case_input_dict = case_input if isinstance(case_input, dict) else {}
        
        # Merge extraction (LLM) with case_input (parser); LLM preferred, parser fallback
        # IMPORTANT: extraction first, then case_input, so parser data FILLS IN empty LLM values
        # But don't overwrite existing extraction values with empty parser lists
        merged_data = {}
        for key in set(list(extraction.keys()) + list(case_input_dict.keys())):
            # Use extraction value if it's non-empty, otherwise use parser value
            ext_val = extraction.get(key)
            parse_val = case_input_dict.get(key)
            if isinstance(ext_val, list) and len(ext_val) > 0:
                merged_data[key] = ext_val  # LLM extraction has data
            elif parse_val is not None:
                merged_data[key] = parse_val  # Parser has data (fallback)
            elif ext_val is not None:
                merged_data[key] = ext_val  # LLM has data (even if empty, use it)
        
        # Debug: Show what we merged
        print(f"[Matcher] Merged data: imaging_findings={len(merged_data.get('imaging_findings', []))}, symptoms={len(merged_data.get('symptoms', []))}, failed_treatments={len(merged_data.get('failed_treatments', []))}")
        
        # Check for imaging correlation
        imaging_findings = merged_data.get("imaging_findings", [])
        if imaging_findings:
            severity = self._assess_imaging_severity(imaging_findings)
            if severity == "severe":
                results.append(CriterionResult(
                    criterion="Imaging Correlation",
                    status="MET",
                    evidence=", ".join(imaging_findings[:2]),
                    gap=None
                ))
            elif severity == "moderate":
                results.append(CriterionResult(
                    criterion="Imaging Correlation",
                    status="PARTIAL",
                    evidence=", ".join(imaging_findings[:2]),
                    gap="Imaging severity assessment incomplete"
                ))
        else:
            results.append(CriterionResult(
                criterion="Imaging Correlation",
                status="NOT_MET",
                evidence="No imaging findings provided",
                gap="Advanced imaging (MRI/CT) required"
            ))
        
        # Check for failed conservative treatment
        failed_treatments = merged_data.get("failed_treatments", [])
        if failed_treatments and len(failed_treatments) >= 2:
            results.append(CriterionResult(
                criterion="Conservative Treatment Failure",
                status="MET",
                evidence=", ".join(failed_treatments[:2]),
                gap=None
            ))
        elif failed_treatments:
            results.append(CriterionResult(
                criterion="Conservative Treatment Failure",
                status="PARTIAL",
                evidence=", ".join(failed_treatments) if failed_treatments else "Limited documentation",
                gap="Additional failed treatment documentation recommended"
            ))
        else:
            results.append(CriterionResult(
                criterion="Conservative Treatment Failure",
                status="NOT_MET",
                evidence="No prior treatment attempts documented",
                gap="History of conservative treatment attempts required"
            ))
        
        # Check for functional impairment documentation
        doc_gaps = merged_data.get("documentation_gaps", [])
        documentation_notes = merged_data.get("documentation_notes", [])
        symptoms = merged_data.get("symptoms", [])
        
        # Check if documentation is COMPLETE (no notes indicating gaps)
        has_doc_gaps = len(doc_gaps) > 0 or any("not explicitly" in str(note).lower() for note in documentation_notes)
        
        if symptoms and len(doc_gaps) == 0 and not has_doc_gaps:
            results.append(CriterionResult(
                criterion="Functional Impairment",
                status="MET",
                evidence=f"Clear documentation of {len(symptoms)} symptoms",
                gap=None
            ))
        elif symptoms or len(doc_gaps) > 0:
            gap_text = ", ".join(doc_gaps) if doc_gaps else "ADL limitations could be more explicit"
            # Add documentation notes to gap if present
            if has_doc_gaps:
                adl_gaps = [note for note in documentation_notes if "ADL" in note or "not explicitly" in note]
                if adl_gaps:
                    gap_text = adl_gaps[0]
            results.append(CriterionResult(
                criterion="Functional Impairment",
                status="PARTIAL",
                evidence=f"Partial documentation: {', '.join(symptoms[:2]) if symptoms else 'limited'}",
                gap=gap_text
            ))
        else:
            results.append(CriterionResult(
                criterion="Functional Impairment",
                status="NOT_MET",
                evidence="No documented functional impairment",
                gap="Clear ADL/IADL limitations required"
            ))
        
        # Check for medical necessity
        requested_service = merged_data.get("requested_service", "")
        documentation_notes = merged_data.get("documentation_notes", [])
        
        # Check for inpatient status gaps in documentation
        inpatient_gap = None
        for note in documentation_notes:
            if "inpatient" in str(note).lower() or "ASC" in str(note):
                inpatient_gap = note
                break
        
        if requested_service and (symptoms or imaging_findings):
            # Check if medical necessity is clear but inpatient justification is incomplete
            if inpatient_gap:
                results.append(CriterionResult(
                    criterion="Medical Necessity",
                    status="PARTIAL",
                    evidence=f"Clear clinical indication: {requested_service}",
                    gap=f"Inpatient status justification: {inpatient_gap}"
                ))
            else:
                results.append(CriterionResult(
                    criterion="Medical Necessity",
                    status="MET",
                    evidence=f"Clear clinical indication: {requested_service}",
                    gap=None
                ))
        else:
            results.append(CriterionResult(
                criterion="Medical Necessity",
                status="PARTIAL",
                evidence="Service requested but justification incomplete",
                gap="Stronger linkage between diagnosis and procedure needed"
            ))
        
        return results

    @staticmethod
    def _assess_imaging_severity(findings: List[str]) -> str:
        """Assess imaging severity based on keywords."""
        severe_keywords = ["severe", "significant", "extensive", "compression", "stenosis", "cord", "myelopathy"]
        moderate_keywords = ["moderate", "mild-moderate", "some", "partial"]
        
        combined_text = " ".join(findings).lower()
        
        severe_count = sum(1 for kw in severe_keywords if kw in combined_text)
        moderate_count = sum(1 for kw in moderate_keywords if kw in combined_text)
        
        if severe_count >= 2:
            return "severe"
        elif severe_count > 0 or moderate_count >= 2:
            return "moderate"
        else:
            return "mild"
