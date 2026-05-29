"use client";

import { MessageSquare } from "lucide-react";

interface ProviderQuestionsProps {
  questions: string[];
}

export default function ProviderQuestions({ questions }: ProviderQuestionsProps) {
  if (questions.length === 0) {
    return null;
  }

  return (
    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
      <div className="flex gap-3">
        <MessageSquare className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h4 className="font-semibold text-purple-900 mb-2">
            Questions for Provider
          </h4>
          <ul className="space-y-2">
            {questions.map((question, idx) => (
              <li key={idx} className="text-sm text-purple-800">
                <span className="font-semibold">Q{idx + 1}:</span> {question}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
