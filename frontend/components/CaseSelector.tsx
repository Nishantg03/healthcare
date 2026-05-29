"use client";

import { ChevronDown } from "lucide-react";
import { useState } from "react";

interface CaseSelectorProps {
  cases: string[];
  selectedCase: string;
  onCaseSelect: (caseId: string) => void;
  isLoading?: boolean;
}

export default function CaseSelector({
  cases,
  selectedCase,
  onCaseSelect,
  isLoading = false,
}: CaseSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative w-full">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Select Case to Analyze
      </label>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isLoading || cases.length === 0}
        className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg shadow-sm text-left flex items-center justify-between hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50 disabled:cursor-not-allowed"
      >
        <span className="text-gray-900">{selectedCase || "Select a case..."}</span>
        <ChevronDown
          className={`w-5 h-5 text-gray-400 transition-transform ${
            isOpen ? "transform rotate-180" : ""
          }`}
        />
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
          {cases.map((caseId) => (
            <button
              key={caseId}
              onClick={() => {
                onCaseSelect(caseId);
                setIsOpen(false);
              }}
              className={`w-full px-4 py-3 text-left hover:bg-blue-50 transition-colors ${
                selectedCase === caseId ? "bg-blue-50 border-l-4 border-blue-500" : ""
              }`}
            >
              {caseId}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
