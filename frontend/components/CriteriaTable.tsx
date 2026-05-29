"use client";

import { Check, X, Minus } from "lucide-react";
import { CriterionResult } from "@/services/api";

interface CriteriaTableProps {
  criteria: CriterionResult[];
}

export default function CriteriaTable({ criteria }: CriteriaTableProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "MET":
        return <Check className="w-5 h-5 text-green-600" />;
      case "PARTIAL":
        return <Minus className="w-5 h-5 text-yellow-600" />;
      case "NOT_MET":
        return <X className="w-5 h-5 text-red-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "MET":
        return "bg-green-50 border-green-200";
      case "PARTIAL":
        return "bg-yellow-50 border-yellow-200";
      case "NOT_MET":
        return "bg-red-50 border-red-200";
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-100 border-b border-gray-200">
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
              Criterion
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 w-24">
              Status
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
              Evidence
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
              Gap
            </th>
          </tr>
        </thead>
        <tbody>
          {criteria.map((criterion, idx) => (
            <tr
              key={idx}
              className={`border-b border-gray-200 ${getStatusColor(
                criterion.status
              )}`}
            >
              <td className="px-4 py-3 text-sm font-medium text-gray-900">
                {criterion.criterion}
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  {getStatusIcon(criterion.status)}
                  <span className="text-sm font-medium text-gray-700">
                    {criterion.status}
                  </span>
                </div>
              </td>
              <td className="px-4 py-3 text-sm text-gray-700">
                {criterion.evidence}
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {criterion.gap ? (
                  <span className="text-yellow-700">{criterion.gap}</span>
                ) : (
                  <span className="text-gray-400">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
