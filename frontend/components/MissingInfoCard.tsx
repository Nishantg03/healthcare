"use client";

import { AlertCircle } from "lucide-react";

interface MissingInfoCardProps {
  missingInfo: string[];
}

export default function MissingInfoCard({ missingInfo }: MissingInfoCardProps) {
  if (missingInfo.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <p className="text-sm text-green-800">✓ No missing information identified</p>
      </div>
    );
  }

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <div className="flex gap-3">
        <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="font-semibold text-yellow-900 mb-2">
            Missing Documentation
          </h4>
          <ul className="space-y-1">
            {missingInfo.map((item, idx) => (
              <li key={idx} className="text-sm text-yellow-800">
                • {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
