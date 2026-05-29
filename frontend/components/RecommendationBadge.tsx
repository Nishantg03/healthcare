"use client";

import { CheckCircle, XCircle, AlertCircle } from "lucide-react";

interface RecommendationBadgeProps {
  recommendation: "LIKELY_APPROVE" | "LIKELY_DENY" | "NEED_MORE_INFO";
  confidence: "HIGH" | "MEDIUM" | "LOW";
}

export default function RecommendationBadge({
  recommendation,
  confidence,
}: RecommendationBadgeProps) {
  const getRecommendationStyles = () => {
    switch (recommendation) {
      case "LIKELY_APPROVE":
        return {
          bgColor: "bg-green-100",
          textColor: "text-green-800",
          borderColor: "border-green-300",
          icon: <CheckCircle className="w-6 h-6" />,
          label: "LIKELY APPROVE",
        };
      case "LIKELY_DENY":
        return {
          bgColor: "bg-red-100",
          textColor: "text-red-800",
          borderColor: "border-red-300",
          icon: <XCircle className="w-6 h-6" />,
          label: "LIKELY DENY",
        };
      case "NEED_MORE_INFO":
        return {
          bgColor: "bg-yellow-100",
          textColor: "text-yellow-800",
          borderColor: "border-yellow-300",
          icon: <AlertCircle className="w-6 h-6" />,
          label: "NEED MORE INFO",
        };
    }
  };

  const getConfidenceBar = () => {
    switch (confidence) {
      case "HIGH":
        return "w-full bg-green-500";
      case "MEDIUM":
        return "w-2/3 bg-yellow-500";
      case "LOW":
        return "w-1/3 bg-red-500";
    }
  };

  const styles = getRecommendationStyles();

  return (
    <div className={`${styles.bgColor} ${styles.borderColor} border rounded-lg p-6`}>
      <div className="flex items-start gap-4">
        <div className={styles.textColor}>{styles.icon}</div>
        <div className="flex-1">
          <h3 className={`${styles.textColor} text-2xl font-bold mb-2`}>
            {styles.label}
          </h3>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm font-medium text-gray-600">
              Confidence: {confidence}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className={`${getConfidenceBar()} h-2 rounded-full`}></div>
          </div>
        </div>
      </div>
    </div>
  );
}
