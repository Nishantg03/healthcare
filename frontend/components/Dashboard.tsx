"use client";

import { useState } from "react";
import { Loader } from "lucide-react";
import UploadBox from "./UploadBox";
import CaseSelector from "./CaseSelector";
import RecommendationBadge from "./RecommendationBadge";
import SummaryCard from "./SummaryCard";
import CriteriaTable from "./CriteriaTable";
import EvidenceList from "./EvidenceList";
import MissingInfoCard from "./MissingInfoCard";
import ProviderQuestions from "./ProviderQuestions";
import apiService, {
  AnalysisResponse,
  UploadResponse,
} from "@/services/api";

export default function Dashboard() {
  const [cases, setCases] = useState<string[]>([]);
  const [selectedCase, setSelectedCase] = useState<string>("");
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const handleFileSelect = async (file: File) => {
    setError("");
    setSuccess("");
    setIsLoading(true);
    setAnalysis(null);
    setSelectedCase("");

    try {
      const response = await apiService.uploadWorkbook(file);
      setCases(response.cases);
      setUploadedFile(file);
      setSuccess(response.message);
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Failed to process workbook. Ensure it has required sheets.";
      setError(errorMessage);
      setCases([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedCase) {
      setError("Please select a case to analyze");
      return;
    }

    setError("");
    setIsLoading(true);

    try {
      const response = await apiService.analyzeCase({ case_id: selectedCase });
      setAnalysis(response);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to analyze case";
      setError(errorMessage);
      setAnalysis(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Healthcare Pre-Auth Copilot
              </h1>
              <p className="text-gray-600 mt-1">
                AI-powered pre-authorization analysis & recommendations
              </p>
            </div>
            <div className="text-right text-sm text-gray-500">
              Production v1.0.0
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Step 1: Upload Workbook
          </h2>
          <UploadBox
            onFileSelect={handleFileSelect}
            isLoading={isLoading}
            error={error && !analysis ? error : undefined}
            success={success && cases.length > 0 ? success : undefined}
          />
        </div>

        {/* Case Selection Section */}
        {cases.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-8 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              Step 2: Select & Analyze Case
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2">
                <CaseSelector
                  cases={cases}
                  selectedCase={selectedCase}
                  onCaseSelect={setSelectedCase}
                  isLoading={isLoading}
                />
              </div>
              <button
                onClick={handleAnalyze}
                disabled={!selectedCase || isLoading}
                className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                {isLoading && <Loader className="w-4 h-4 animate-spin" />}
                Analyze Case
              </button>
            </div>
          </div>
        )}

        {/* Analysis Results Section */}
        {analysis && (
          <div className="space-y-8">
            {/* Recommendation Badge */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <RecommendationBadge
                recommendation={analysis.recommendation}
                confidence={analysis.confidence}
              />
            </div>

            {/* Clinical Summary */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <SummaryCard summary={analysis.clinical_summary} />
            </div>

            {/* Criteria Matching */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">
                Approval Criteria Evaluation
              </h3>
              <CriteriaTable criteria={analysis.criteria_results} />
            </div>

            {/* Supporting Evidence & Missing Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Supporting Evidence
                </h3>
                <EvidenceList evidence={analysis.supporting_evidence} />
              </div>

              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Documentation Gaps
                </h3>
                <MissingInfoCard missingInfo={analysis.missing_information} />
              </div>
            </div>

            {/* Provider Questions */}
            {analysis.provider_questions.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <ProviderQuestions questions={analysis.provider_questions} />
              </div>
            )}

            {/* Denial Risks */}
            {analysis.denial_risks && analysis.denial_risks.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Denial Risks
                </h3>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <ul className="space-y-2">
                    {analysis.denial_risks.map((risk, idx) => (
                      <li key={idx} className="text-sm text-red-800">
                        ⚠ {risk}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Case Info Footer */}
            <div className="bg-gray-50 rounded-lg border border-gray-200 p-6 text-center">
              <p className="text-sm text-gray-600">
                Case ID: <span className="font-mono font-semibold">{analysis.case_id}</span>
              </p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && !analysis && (
          <div className="bg-white rounded-lg shadow-md p-12 flex flex-col items-center justify-center">
            <Loader className="w-8 h-8 text-blue-600 animate-spin mb-4" />
            <p className="text-gray-600 font-medium">
              Analyzing case with AI reasoning engine...
            </p>
            <p className="text-sm text-gray-500 mt-2">
              This may take a moment as we evaluate all criteria
            </p>
          </div>
        )}

        {/* Empty State */}
        {!cases.length && !analysis && !isLoading && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="mb-4 text-5xl">📋</div>
            <p className="text-gray-600 text-lg">
              Upload an Excel workbook to get started
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 text-center py-4 mt-12 text-sm">
        Healthcare Pre-Authorization Copilot | Powered by Groq AI
      </footer>
    </div>
  );
}
