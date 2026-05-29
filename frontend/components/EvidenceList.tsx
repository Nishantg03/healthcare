"use client";

import { CheckCircle } from "lucide-react";

interface EvidenceListProps {
  evidence: string[];
}

export default function EvidenceList({ evidence }: EvidenceListProps) {
  if (evidence.length === 0) {
    return (
      <div className="text-gray-500 text-sm italic">
        No supporting evidence documented
      </div>
    );
  }

  return (
    <ul className="space-y-2">
      {evidence.map((item, idx) => (
        <li key={idx} className="flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <span className="text-gray-700 text-sm">{item}</span>
        </li>
      ))}
    </ul>
  );
}
