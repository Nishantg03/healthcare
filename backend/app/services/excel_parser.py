import pandas as pd
from typing import Dict, List, Any
import json
import re


class ExcelParser:
    """Parse healthcare pre-authorization Excel workbooks.
    
    Each sheet has semantic purpose:
    - Problem_Statement: Ignored (assignment instructions only)
    - Training_Cases: Few-shot examples for LLM
    - Patient_Data_Aspects: Schema definition for normalized extraction
    - Complex_Case_Input: Main patient case (converted to structured JSON)
    - Complex_Case_Outcome: Approval criteria definitions
    - Suggested_Output: Expected response structure
    """

    REQUIRED_SHEETS = [
        "Problem_Statement",
        "Training_Cases",
        "Patient_Data_Aspects",
        "Complex_Case_Input",
        "Complex_Case_Outcome",
        "Suggested_Output"
    ]

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.excel_file = pd.ExcelFile(file_path)
        self.sheets = self.excel_file.sheet_names

    def validate_workbook(self) -> bool:
        """Validate that required sheets exist."""
        missing_sheets = [s for s in self.REQUIRED_SHEETS if s not in self.sheets]
        if missing_sheets:
            raise ValueError(f"Missing required sheets: {missing_sheets}")
        return True


    def _normalize_symptoms(self, case_input: Dict) -> List[str]:
        """Extract symptoms into normalized list."""
        symptoms = []
        
        if isinstance(case_input, dict):
            # Check symptoms section
            if "symptoms" in case_input and isinstance(case_input["symptoms"], dict):
                for key, value in case_input["symptoms"].items():
                    if value and value.strip():
                        # Parse comma-separated symptoms
                        if key == "chief_symptoms" or key == "pain_severity" or key == "chief_complaint":
                            symptom_list = [s.strip() for s in str(value).split(",")]
                            symptoms.extend([s for s in symptom_list if s])
            
            # Also check function section for ADL-related symptoms
            if "function" in case_input and isinstance(case_input["function"], dict):
                for key, value in case_input["function"].items():
                    if value and "adl" in key.lower():
                        # Parse ADL impacts
                        adl_list = [s.strip() for s in str(value).split(",")]
                        symptoms.extend([s for s in adl_list if s])
        
        return symptoms

    def _normalize_imaging_findings(self, case_input: Dict) -> List[str]:
        """Extract imaging findings into normalized list."""
        findings = []
        
        if isinstance(case_input, dict) and "imaging" in case_input:
            imaging_section = case_input["imaging"]
            if isinstance(imaging_section, dict):
                for key, value in imaging_section.items():
                    if value and value.strip():
                        # Split by semicolon or comma for multiple findings
                        finding_list = re.split(r'[;,]', str(value))
                        findings.extend([f.strip() for f in finding_list if f.strip()])
        
        return findings

    def _normalize_treatments(self, case_input: Dict) -> List[str]:
        """Extract failed treatments into normalized list."""
        treatments = []
        
        if isinstance(case_input, dict) and "treatment_history" in case_input:
            th_section = case_input["treatment_history"]
            if isinstance(th_section, dict):
                for key, value in th_section.items():
                    if value and value.strip():
                        # Skip response/outcome fields, get the actual treatments
                        if "conservative" in key.lower() or "care" in key.lower():
                            # Parse comma-separated treatments
                            treatment_list = [t.strip() for t in str(value).split(",")]
                            treatments.extend([t for t in treatment_list if t])
        
        return treatments

    def _normalize_documentation_notes(self, case_input: Dict) -> List[str]:
        """Extract documentation gaps and quality notes."""
        notes = []
        
        if isinstance(case_input, dict) and "administrative" in case_input:
            admin_section = case_input["administrative"]
            if isinstance(admin_section, dict):
                for key, value in admin_section.items():
                    if value and value.strip():
                        notes.append(str(value).strip())
        
        return notes

    def _extract_patient_demographics(self, case_input: Dict) -> Dict[str, Any]:
        """Extract patient demographics."""
        patient = {
            "age": None,
            "gender": None,
            "risk_factors": []
        }
        
        if isinstance(case_input, dict):
            # Demographics section
            if "demographics" in case_input and isinstance(case_input["demographics"], dict):
                demo = case_input["demographics"]
                if "age_sex" in demo:
                    # Parse "58 / Male" format
                    age_sex = demo["age_sex"]
                    parts = str(age_sex).split("/")
                    if len(parts) >= 1:
                        try:
                            patient["age"] = int(parts[0].strip())
                        except:
                            pass
                    if len(parts) >= 2:
                        patient["gender"] = parts[1].strip()
            
            # Risk factors from comorbidities
            if "comorbidities" in case_input and isinstance(case_input["comorbidities"], dict):
                comorbidities = case_input["comorbidities"]
                if "medical_risk_factors" in comorbidities:
                    risk_str = comorbidities["medical_risk_factors"]
                    risk_list = [r.strip() for r in str(risk_str).split(",")]
                    patient["risk_factors"] = [r for r in risk_list if r]
        
        return patient

    def _extract_request_info(self, case_input: Dict) -> Dict[str, Any]:
        """Extract requested service and diagnosis."""
        request_info = {
            "requested_service": None,
            "primary_diagnosis": None,
            "payer_policy": None
        }
        
        if isinstance(case_input, dict) and "request" in case_input:
            req_section = case_input["request"]
            if isinstance(req_section, dict):
                # Try all possible key variations
                for key, value in req_section.items():
                    key_lower = key.lower()
                    if "requested_service" in key_lower or "service" in key_lower:
                        request_info["requested_service"] = value
                    elif "diagnosis" in key_lower:
                        request_info["primary_diagnosis"] = value
                    elif "payer" in key_lower or "policy" in key_lower:
                        request_info["payer_policy"] = value
        
        # Fallback: try to extract from raw notes if not found
        if not request_info["requested_service"] and isinstance(case_input, dict):
            if "administrative" in case_input and isinstance(case_input["administrative"], dict):
                for key, value in case_input["administrative"].items():
                    # Look for service in notes
                    if isinstance(value, str) and "decompression" in value.lower():
                        request_info["requested_service"] = value.split("\n")[0]
                        break
        
        return request_info

  
    # SHEET PARSING FUNCTIONS (semantic processors)

    
    def parse_training_cases(self) -> List[Dict[str, Any]]:
        """Parse Training_Cases sheet into few-shot examples.
        
        Returns list of normalized training examples for LLM context.
        """
        training_examples = []
        
        try:
            df = pd.read_excel(self.file_path, sheet_name="Training_Cases")
            
            # Convert to list of dicts
            for idx, row in df.iterrows():
                example = {}
                for col in df.columns:
                    val = row[col]
                    # Clean NaN values
                    if pd.notna(val):
                        example[col.lower().replace(" ", "_")] = str(val).strip()
                
                if example:  # Only add non-empty rows
                    training_examples.append(example)
        
        except Exception as e:
            print(f"Error parsing Training_Cases: {e}")
        
        return training_examples

    def parse_patient_schema(self) -> Dict[str, Any]:
        """Parse Patient_Data_Aspects to define extraction schema."""
        schema = {
            "patient": {},
            "symptoms": [],
            "imaging_findings": [],
            "failed_treatments": [],
            "documentation_notes": [],
            "requested_service": None,
            "risk_factors": []
        }
        
        try:
            df = pd.read_excel(self.file_path, sheet_name="Patient_Data_Aspects")
            # Store as reference for extraction guidance
            schema["schema_reference"] = df.to_dict("records")
        except Exception as e:
            print(f"Error parsing Patient_Data_Aspects: {e}")
        
        return schema

    def parse_complex_case(self, case_id: str) -> Dict[str, Any]:
        """Parse Complex_Case_Input into normalized structured JSON.
        
        This is the MAIN patient case for analysis - fully normalized.
        """
        case_data = {
            "case_id": case_id,
            "patient": {},
            "requested_service": None,
            "primary_diagnosis": None,
            "symptoms": [],
            "imaging_findings": [],
            "failed_treatments": [],
            "risk_factors": [],
            "documentation_notes": [],
            "raw_input": {}  # Keep raw for reference
        }
        
        try:
            # Read with headers=None to handle mixed format
            raw_df = pd.read_excel(self.file_path, sheet_name="Complex_Case_Input", header=None)
            
            # Convert to nested dict format (Section/Field/Value)
            section_dict = self._parse_section_field_value_format(raw_df)
            case_data["raw_input"] = section_dict
            
            # Now normalize the extracted data
            if section_dict:
                # Extract demographics
                patient_info = self._extract_patient_demographics(section_dict)
                case_data["patient"] = patient_info
                
                # Extract request info
                request_info = self._extract_request_info(section_dict)
                case_data["requested_service"] = request_info.get("requested_service")
                case_data["primary_diagnosis"] = request_info.get("primary_diagnosis")
                
                # Extract normalized lists
                case_data["symptoms"] = self._normalize_symptoms(section_dict)
                case_data["imaging_findings"] = self._normalize_imaging_findings(section_dict)
                case_data["failed_treatments"] = self._normalize_treatments(section_dict)
                case_data["documentation_notes"] = self._normalize_documentation_notes(section_dict)
                
                # Extract risk factors
                if "comorbidities" in section_dict and isinstance(section_dict["comorbidities"], dict):
                    comorbidities = section_dict["comorbidities"]
                    if "medical_risk_factors" in comorbidities:
                        risk_str = comorbidities["medical_risk_factors"]
                        case_data["risk_factors"] = [r.strip() for r in str(risk_str).split(",") if r.strip()]
        
        except Exception as e:
            print(f"Error parsing complex case: {e}")
        
        return case_data

    def parse_criteria(self) -> Dict[str, List[Dict[str, str]]]:
        """Parse Complex_Case_Outcome into criteria definitions.
        
        Returns dict mapping criterion IDs to criteria definitions.
        """
        criteria = {}
        
        try:
            raw_df = pd.read_excel(self.file_path, sheet_name="Complex_Case_Outcome", header=None)
            
            # Find criteria rows (starts with C and has status)
            for idx in range(len(raw_df)):
                row = raw_df.iloc[idx]
                criterion_id = str(row.iloc[0]).strip() if not pd.isna(row.iloc[0]) else None
                policy_criterion = str(row.iloc[1]).strip() if len(row) > 1 and not pd.isna(row.iloc[1]) else None
                status = str(row.iloc[2]).strip() if len(row) > 2 and not pd.isna(row.iloc[2]) else None
                
                # Valid criteria start with C and have MET/PARTIAL/NOT_MET status
                if criterion_id and criterion_id.startswith("C") and status in ["MET", "PARTIAL", "NOT_MET"]:
                    criteria[criterion_id] = {
                        "criterion": policy_criterion or "",
                        "status": status,
                        "evidence": str(row.iloc[3]).strip() if len(row) > 3 else "",
                        "gap": str(row.iloc[4]).strip() if len(row) > 4 else ""
                    }
        
        except Exception as e:
            print(f"Error parsing criteria: {e}")
        
        return criteria

    def parse_output_schema(self) -> Dict[str, Any]:
        """Parse Suggested_Output sheet for expected response structure."""
        schema = {}
        
        try:
            df = pd.read_excel(self.file_path, sheet_name="Suggested_Output")
            schema = df.to_dict("records")
        except Exception as e:
            print(f"Error parsing output schema: {e}")
        
        return schema
   # HELPER FUNCTIONS
      
    def _parse_section_field_value_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Convert Section/Field/Value format to nested dict."""
        result = {}
        
        # Find header row
        header_row = None
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            if not pd.isna(row.iloc[0]) and "Section" in str(row.iloc[0]):
                header_row = i
                break
        
        if header_row is None:
            return result
        
        # Parse data rows
        for idx in range(header_row + 1, len(df)):
            row = df.iloc[idx]
            section_raw = str(row.iloc[0]).strip() if not pd.isna(row.iloc[0]) else None
            field_raw = str(row.iloc[1]).strip() if len(row) > 1 and not pd.isna(row.iloc[1]) else None
            value = str(row.iloc[2]).strip() if len(row) > 2 and not pd.isna(row.iloc[2]) else None
            
            # Skip if no data
            if not section_raw or not field_raw or not value or value == "nan":
                continue
            
            # Normalize section name
            section_key = section_raw.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
            
            # Initialize section if needed
            if section_key not in result:
                result[section_key] = {}
            
            # Normalize field name
            field_key = field_raw.lower().replace(" / ", "_").replace(" & ", "_and_").replace(" - ", "_").replace(" ", "_")
            
            # Store value
            result[section_key][field_key] = value
        
        return result


    # ============================================================================
    # PUBLIC API - HIGH LEVEL METHODS
    # ============================================================================
    
    def get_all_cases(self) -> List[str]:
        """Extract all PA case IDs from workbook."""
        case_ids = []
        
        # Get training cases
        try:
            training_df = pd.read_excel(self.file_path, sheet_name="Training_Cases")
            if "PA_ID" in training_df.columns or "Case_ID" in training_df.columns:
                col_name = "PA_ID" if "PA_ID" in training_df.columns else "Case_ID"
                case_ids.extend(training_df[col_name].dropna().unique().tolist())
        except Exception as e:
            print(f"Error reading Training_Cases: {e}")
        
        # Get complex case ID
        try:
            complex_df = pd.read_excel(self.file_path, sheet_name="Complex_Case_Input", header=None)
            if len(complex_df) > 0:
                first_cell = str(complex_df.iloc[0, 0]) if not pd.isna(complex_df.iloc[0, 0]) else ""
                if "PA-" in first_cell:
                    pa_id = first_cell.split("PA-")[1].split()[0]
                    case_ids.append(f"PA-{pa_id}")
                else:
                    case_ids.append("COMPLEX_CASE")
        except Exception as e:
            print(f"Error reading Complex_Case_Input: {e}")
        
        return list(set(case_ids))

    def get_case_data(self, case_id: str) -> Dict[str, Any]:
        """Extract fully normalized case data for analysis.
        
        Returns structured JSON with:
        - Normalized patient case (for LLM analysis)
        - Training examples (for few-shot context)
        - Approval criteria (for deterministic matching)
        - Schema reference (for validation)
        """
        return {
            "case_id": case_id,
            "case_input": self.parse_complex_case(case_id),
            "training_cases": self.parse_training_cases(),
            "approval_criteria": self.parse_criteria(),
            "data_aspects": self.parse_patient_schema(),
            "output_schema": self.parse_output_schema()
        }

    def get_suggested_output_schema(self) -> Dict[str, Any]:
        """Get the expected output schema."""
        return self.parse_output_schema()
