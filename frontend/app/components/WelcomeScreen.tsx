"use client";

import React from "react";
import Logo from "./Logo";
import SmartAssessmentSection from "./SmartAssessmentSection";
import { ChatMode, AssessmentData } from "../types";
import { Language, translations } from "../i18n";

interface WelcomeScreenProps {
  mode: ChatMode;
  language: Language;
  onSelectPrompt: (prompt: string) => void;
  onAnalyzeProduct: (productDescription: string) => Promise<void>;
  isAssessmentLoading: boolean;
  assessmentResult: AssessmentData | null;
  onAskFollowUp: (query: string) => void;
  onResetAssessment: () => void;
  disabled?: boolean;
}

export default function WelcomeScreen({
  mode,
  language,
  onSelectPrompt,
  onAnalyzeProduct,
  isAssessmentLoading,
  assessmentResult,
  onAskFollowUp,
  onResetAssessment,
  disabled = false,
}: WelcomeScreenProps) {
  const t = translations[language];
  // Ensure exactly three suggestions are displayed
  const suggestions = (t.suggestions[mode] || []).slice(0, 3);

  return (
    <div className="relative flex flex-col items-center justify-center text-center max-w-2xl mx-auto px-4 py-6 sm:py-10 animate-in fade-in duration-300">
      {/* Central Welcome Hero */}
      <div className="relative flex flex-col items-center">
        {/* Soft focal halo behind logo */}
        <div
          className="absolute -top-6 w-24 h-24 rounded-full blur-xl opacity-60 dark:opacity-40"
          style={{
            background: "radial-gradient(circle, rgba(59, 130, 246, 0.4), transparent 70%)",
          }}
          aria-hidden="true"
        />

        {/* Original BIS Sahayak Mark */}
        <div className="relative mb-3.5">
          <Logo size="lg" />
        </div>

        {/* Product Name */}
        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-slate-900 dark:text-white">
          {t.welcome.title}
        </h1>

        {/* Concise Subtitle */}
        <p className="mt-2 text-sm sm:text-base text-slate-600 dark:text-slate-400 font-normal max-w-md leading-relaxed">
          {t.welcome.subtitle}
        </p>
      </div>

      {/* PROMINENT FEATURE: BIS Smart Assessment ("Find My BIS Requirements") */}
      <div className="w-full mt-4 sm:mt-5">
        <SmartAssessmentSection
          onAnalyze={onAnalyzeProduct}
          isLoading={isAssessmentLoading}
          assessmentResult={assessmentResult}
          onAskFollowUp={onAskFollowUp}
          onReset={onResetAssessment}
          disabled={disabled}
        />
      </div>

      {/* "Try asking" with exactly THREE minimal pill suggestions */}
      {!assessmentResult && (
        <div className="mt-4 w-full flex flex-col items-center">
          <span className="text-[11px] font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2.5">
            {t.welcome.tryAsking}
          </span>

          <div className="flex flex-wrap items-center justify-center gap-2 max-w-lg">
            {suggestions.map((question, index) => (
              <button
                key={index}
                type="button"
                onClick={() => onSelectPrompt(question)}
                disabled={disabled}
                className="inline-flex items-center px-3.5 py-1.5 rounded-full text-xs font-medium text-slate-700 dark:text-slate-300 bg-white/90 dark:bg-slate-900/80 border border-slate-200/90 dark:border-slate-800 hover:border-blue-500/60 dark:hover:border-blue-500/60 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50/30 dark:hover:bg-blue-950/20 transition-all duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shadow-2xs backdrop-blur-xs focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-blue-500"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
