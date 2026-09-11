"use client";

import React, { useState } from "react";
import ProductAssessmentCard from "./ProductAssessmentCard";
import { AssessmentData } from "../types";

interface SmartAssessmentSectionProps {
  onAnalyze: (productDescription: string) => Promise<void>;
  isLoading: boolean;
  assessmentResult: AssessmentData | null;
  onAskFollowUp: (query: string) => void;
  onReset: () => void;
  disabled?: boolean;
}

export default function SmartAssessmentSection({
  onAnalyze,
  isLoading,
  assessmentResult,
  onAskFollowUp,
  onReset,
  disabled = false,
}: SmartAssessmentSectionProps) {
  const [productInput, setProductInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = productInput.trim();
    if (!trimmed || isLoading || disabled) return;
    onAnalyze(trimmed);
  };

  const handleSelectExample = (example: string) => {
    setProductInput(example);
    onAnalyze(example);
  };

  // If we have an assessment result, render the official Assessment Card!
  if (assessmentResult) {
    return (
      <div className="w-full max-w-2xl mx-auto my-4 animate-in fade-in slide-in-from-bottom-3 duration-250">
        <ProductAssessmentCard
          data={assessmentResult}
          onAskFollowUp={onAskFollowUp}
          onReset={() => {
            setProductInput("");
            onReset();
          }}
        />
      </div>
    );
  }

  return (
    <div className="w-full max-w-xl mx-auto my-4 text-left">
      <div className="relative rounded-2xl p-5 sm:p-6 border border-blue-200/90 dark:border-blue-900/60 bg-gradient-to-b from-blue-50/90 via-white/95 to-slate-50/90 dark:from-blue-950/40 dark:via-[#131822]/95 dark:to-[#0F141D]/90 shadow-md shadow-blue-500/5 dark:shadow-black/30 backdrop-blur-md transition-all duration-200">
        {/* Accent glow corner */}
        <div
          className="absolute top-0 right-0 w-32 h-32 rounded-tr-2xl pointer-events-none opacity-40 dark:opacity-20 blur-2xl"
          style={{
            background:
              "radial-gradient(circle, rgba(37,99,235,0.4) 0%, transparent 70%)",
          }}
          aria-hidden="true"
        />

        {/* Top Header & Badge */}
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-100/90 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 border border-blue-300/60 dark:border-blue-700/50">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-600 dark:bg-blue-400" />
            BIS Smart Assessment
          </div>
          <span className="text-[10px] font-medium text-slate-500 dark:text-slate-400">
            Compliance Engine
          </span>
        </div>

        {/* Main Title & Subtitle */}
        <h2 className="text-lg sm:text-xl font-bold tracking-tight text-slate-900 dark:text-white">
          Find My BIS Requirements
        </h2>
        <p className="mt-1 text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          Identify applicable Indian Standards and BIS certification pathways for your product.
        </p>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-4 space-y-3">
          <div>
            <label
              htmlFor="product-assessment-input"
              className="block text-xs font-semibold text-slate-700 dark:text-slate-200 mb-1.5"
            >
              Describe your product
            </label>
            <div className="relative flex items-center">
              <input
                id="product-assessment-input"
                type="text"
                value={productInput}
                onChange={(e) => setProductInput(e.target.value)}
                placeholder="e.g. Domestic pressure cooker"
                disabled={isLoading || disabled}
                className="w-full pl-3.5 pr-28 py-2.5 text-sm rounded-xl border border-slate-300/90 dark:border-slate-700 bg-white dark:bg-slate-900/90 text-slate-900 dark:text-white placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 shadow-2xs transition-all disabled:opacity-60"
              />

              <button
                type="submit"
                disabled={!productInput.trim() || isLoading || disabled}
                className="absolute right-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:opacity-40 disabled:cursor-not-allowed shadow-xs transition-all flex items-center gap-1.5 cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <span>Analyze Product</span>
                    <svg
                      className="w-3.5 h-3.5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M13 7l5 5m0 0l-5 5m5-5H6"
                      />
                    </svg>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Quick Example Chips */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
              Quick test:
            </span>
            <button
              type="button"
              onClick={() => handleSelectExample("Domestic pressure cooker")}
              disabled={isLoading || disabled}
              className="inline-flex items-center px-2.5 py-1 rounded-lg text-[11px] font-medium bg-white/80 dark:bg-slate-800/80 hover:bg-blue-50 dark:hover:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-slate-200/80 dark:border-slate-700 transition-colors cursor-pointer"
            >
              Domestic pressure cooker
            </button>
            <button
              type="button"
              onClick={() => handleSelectExample("Rubber Gaskets for Pressure Cookers")}
              disabled={isLoading || disabled}
              className="inline-flex items-center px-2.5 py-1 rounded-lg text-[11px] font-medium bg-white/80 dark:bg-slate-800/80 hover:bg-blue-50 dark:hover:bg-blue-950/40 text-slate-700 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700 transition-colors cursor-pointer"
            >
              IS 7466 (Rubber Gaskets)
            </button>
          </div>
        </form>

        {/* Live analyzing scan status indicator */}
        {isLoading && (
          <div className="mt-4 p-3 rounded-xl bg-blue-500/10 dark:bg-blue-500/15 border border-blue-500/20 flex items-center gap-3 animate-pulse">
            <div className="w-5 h-5 rounded-full border-2 border-blue-600 border-t-transparent animate-spin shrink-0" />
            <div className="text-xs text-blue-800 dark:text-blue-200">
              <div className="font-semibold">
                Scanning official BIS database & Product Certification Schemes...
              </div>
              <div className="text-[11px] opacity-80">
                Retrieving applicable Indian Standards and Simplified Procedure entries.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
