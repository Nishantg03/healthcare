"use client";

interface SummaryCardProps {
  summary: string;
}

export default function SummaryCard({ summary }: SummaryCardProps) {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Clinical Summary</h3>
      <p className="text-gray-700 leading-relaxed">{summary}</p>
    </div>
  );
}
