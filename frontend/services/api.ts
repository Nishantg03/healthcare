import axios, { AxiosInstance } from "axios";

export interface UploadResponse {
  cases: string[];
  message: string;
}

export interface CriterionResult {
  criterion: string;
  status: "MET" | "PARTIAL" | "NOT_MET";
  evidence: string;
  gap?: string;
}

export interface AnalysisResponse {
  case_id: string;
  recommendation: "LIKELY_APPROVE" | "LIKELY_DENY" | "NEED_MORE_INFO";
  confidence: "HIGH" | "MEDIUM" | "LOW";
  clinical_summary: string;
  criteria_results: CriterionResult[];
  supporting_evidence: string[];
  missing_information: string[];
  provider_questions: string[];
  denial_risks?: string[];
}

export interface AnalyzeRequest {
  case_id: string;
}

class ApiService {
  private client: AxiosInstance;

  constructor(baseURL: string = "http://localhost:8000") {
    this.client = axios.create({
      baseURL,
    });
  }

  async uploadWorkbook(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await this.client.post<UploadResponse>(
        "/api/upload",
        formData
      );
      return response.data;
    } catch (error: any) {
      console.error("Upload error details:", error.response?.data || error.message);
      throw error;
    }
  }

  async setWorkbook(file: File): Promise<{ message: string }> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await this.client.post<{ message: string }>(
      "/api/set-workbook",
      formData
    );
    return response.data;
  }

  async analyzeCase(request: AnalyzeRequest): Promise<AnalysisResponse> {
    const response = await this.client.post<AnalysisResponse>(
      "/api/analyze",
      request
    );
    return response.data;
  }

  async analyzeCaseInline(
    file: File,
    caseId: string = "COMPLEX_CASE"
  ): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await this.client.post<AnalysisResponse>(
      `/api/analyze-inline?case_id=${caseId}`,
      formData
    );
    return response.data;
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get("/health");
    return response.data;
  }
}

export default new ApiService();
