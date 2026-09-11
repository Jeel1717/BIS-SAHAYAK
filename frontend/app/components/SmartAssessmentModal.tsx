"use client";

import React from "react";
import SmartAssessmentSection from "./SmartAssessmentSection";
import { AssessmentData } from "../types";

interface SmartAssessmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAnalyze: (productDescription: string) => Promise<void>;
  isLoading: boolean;
  assessmentResult: AssessmentData | null;
  onAskFollowUp: (query: string) => void;
  onReset: () => void;
}

export default function SmartAssessmentModal({
  isOpen,
  onClose,
  onAnalyze,
  isLoading,
  assessmentResult,
  onAskFollowUp,
  onReset,
}: SmartAssessmentModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl bg-white dark:bg-[#0F141D] border border-slate-200/90 dark:border-slate-800 shadow-2xl p-4 sm:p-6">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-4 right-4 w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 flex items-center justify-center text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer"
        >
          ✕
        </button>

        <div className="pt-2">
          <SmartAssessmentSection
            onAnalyze={onAnalyze}
            isLoading={isLoading}
            assessmentResult={assessmentResult}
            onAskFollowUp={(query) => {
              onAskFollowUp(query);
              onClose();
            }}
            onReset={onReset}
          />
        </div>
      </div>
    </div>
  );
}
