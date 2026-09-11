"use client";

import React, { useState } from "react";
import { AssessmentData } from "../types";

interface ProductAssessmentCardProps {
  data: AssessmentData;
  onAskFollowUp?: (query: string) => void;
  onReset?: () => void;
}

export default function ProductAssessmentCard({
  data,
  onAskFollowUp,
  onReset,
}: ProductAssessmentCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const summary = `BIS SMART ASSESSMENT
--------------------------------
PRODUCT IDENTIFIED:
${data.productIdentified}

APPLICABLE STANDARD:
${data.applicableStandard}${data.standardTitle ? `\n${data.standardTitle}` : ""}

CERTIFICATION PATHWAY:
${data.certificationPathway}

PROCEDURE:
${data.procedure}

EVIDENCE:
${data.evidenceSource}
${data.evidenceItem || "Item 187"}

NEXT STEP:
${data.nextStep}
--------------------------------
Official source: ${data.sourceUrl || "https://www.bis.gov.in"}`;

    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!data.foundInformation) {
    return (
      <div className="w-full rounded-2xl border border-amber-200/90 dark:border-amber-900/60 bg-white/95 dark:bg-[#121720]/95 shadow-lg shadow-amber-900/5 dark:shadow-black/40 overflow-hidden backdrop-blur-md transition-all duration-200 animate-in fade-in zoom-in-95">
        <div className="h-1 w-full bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600" />
        <div className="px-5 sm:px-6 py-4 border-b border-slate-100 dark:border-slate-800/80 bg-slate-50/70 dark:bg-[#161C26]/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-amber-600/10 dark:bg-amber-500/15 text-amber-600 dark:text-amber-400 flex items-center justify-center font-bold text-base border border-amber-500/20 shadow-xs">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold tracking-widest text-amber-700 dark:text-amber-400 uppercase">
                  Bureau of Indian Standards
                </span>
                <span className="inline-block w-1 h-1 rounded-full bg-slate-300 dark:bg-slate-700" />
                <span className="text-[10px] font-medium text-slate-500 dark:text-slate-400">
                  Assessment Gate
                </span>
              </div>
              <h2 className="text-base sm:text-lg font-bold tracking-tight text-slate-900 dark:text-white uppercase">
                BIS SMART ASSESSMENT
              </h2>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200/80 dark:border-amber-800/80">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
              Insufficient Official Evidence
            </span>
          </div>
        </div>

        <div className="p-5 sm:p-6 space-y-4 text-left">
          <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-900/60 border border-slate-200/70 dark:border-slate-800/80">
            <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 tracking-wider uppercase mb-1">
              PRODUCT EVALUATED
            </div>
            <div className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
              {data.productIdentified}
            </div>
          </div>

          <div className="p-4 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/70 dark:border-amber-900/40">
            <div className="text-[11px] font-bold text-amber-800 dark:text-amber-400 tracking-wider uppercase mb-1">
              FINDING: NO RELEVANT STANDARD IN CURRENTLY INDEXED RECORDS
            </div>
            <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              The 24 official BIS public documents currently indexed in the BIS Sahayak knowledge base do not contain verified certification entries or Indian Standards for <strong>&quot;{data.productIdentified}&quot;</strong>.
            </p>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
              <strong>Grounding Rule:</strong> BIS Sahayak strictly adheres to verified official evidence and never infers or fabricates certification requirements without authoritative documentation.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-900/60 border border-slate-200/70 dark:border-slate-800/80">
            <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 tracking-wider uppercase mb-1.5">
              RECOMMENDED NEXT ACTIONS
            </div>
            <ul className="text-xs text-slate-600 dark:text-slate-300 space-y-1.5 list-disc pl-4">
              <li>Search the official BIS Standards Portal: <a href="https://www.services.bis.gov.in" target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 underline underline-offset-2">services.bis.gov.in</a></li>
              <li>Consult the National Standards Portal (Know Your Standard - KYS).</li>
              <li>Contact the BIS National Helpdesk at <strong>1800-11-4000</strong>.</li>
            </ul>
          </div>
        </div>

        <div className="px-5 sm:px-6 py-3.5 border-t border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-[#161C26]/50 flex flex-wrap items-center justify-between gap-2">
          {onReset && (
            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/30 transition-colors cursor-pointer"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Assess Another Product</span>
            </button>
          )}

          {onAskFollowUp && (
            <button
              type="button"
              onClick={() => onAskFollowUp(`What BIS standards or certifications might exist for ${data.productIdentified}?`)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200/60 dark:hover:bg-slate-800/80 transition-colors cursor-pointer"
            >
              <span>Ask BIS Sahayak in Chat</span>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full rounded-2xl border border-slate-200/90 dark:border-slate-800 bg-white/95 dark:bg-[#121720]/95 shadow-lg shadow-blue-900/5 dark:shadow-black/40 overflow-hidden backdrop-blur-md transition-all duration-200 animate-in fade-in zoom-in-95">
      {/* Top National / Regulatory Accent Bar */}
      <div className="h-1 w-full bg-gradient-to-r from-orange-500 via-blue-600 to-emerald-600" />

      {/* Card Header */}
      <div className="px-5 sm:px-6 py-4 border-b border-slate-100 dark:border-slate-800/80 bg-slate-50/70 dark:bg-[#161C26]/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600/10 dark:bg-blue-500/15 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-base border border-blue-500/20 shadow-xs">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold tracking-widest text-blue-600 dark:text-blue-400 uppercase">
                Bureau of Indian Standards
              </span>
              <span className="inline-block w-1 h-1 rounded-full bg-slate-300 dark:bg-slate-700" />
              <span className="text-[10px] font-medium text-slate-500 dark:text-slate-400">
                Decision Support System
              </span>
            </div>
            <h2 className="text-base sm:text-lg font-bold tracking-tight text-slate-900 dark:text-white uppercase">
              BIS SMART ASSESSMENT
            </h2>
          </div>
        </div>

        {/* Evidence Badge */}
        <div className="flex items-center gap-2 shrink-0">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200/80 dark:border-emerald-800/80">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Official Evidence Grounded
          </span>
        </div>
      </div>

      {/* Card Content Grid */}
      <div className="p-5 sm:p-6 space-y-4">
        {/* 1. PRODUCT IDENTIFIED */}
        <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-900/60 border border-slate-200/70 dark:border-slate-800/80">
          <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 tracking-wider uppercase mb-1">
            PRODUCT IDENTIFIED
          </div>
          <div className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
            {data.productIdentified}
          </div>
        </div>

        {/* 2-Column Grid for Standard & Pathway */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* 2. APPLICABLE STANDARD */}
          <div className="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-950/20 border border-blue-200/70 dark:border-blue-900/40">
            <div className="text-[11px] font-bold text-blue-700 dark:text-blue-400 tracking-wider uppercase mb-1 flex items-center justify-between">
              <span>APPLICABLE STANDARD</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900/60 font-semibold">
                Mandatory
              </span>
            </div>
            <div className="text-lg font-extrabold text-blue-900 dark:text-blue-100">
              {data.applicableStandard}
            </div>
            {data.standardTitle && (
              <div className="text-xs sm:text-sm font-medium text-slate-600 dark:text-slate-300 mt-0.5">
                {data.standardTitle}
              </div>
            )}
          </div>

          {/* 3. CERTIFICATION PATHWAY */}
          <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-900/60 border border-slate-200/70 dark:border-slate-800/80">
            <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 tracking-wider uppercase mb-1">
              CERTIFICATION PATHWAY
            </div>
            <div className="text-sm sm:text-base font-bold text-slate-900 dark:text-white">
              {data.certificationPathway}
            </div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
              Standard Mark Licensing (ISI Mark)
            </div>
          </div>
        </div>

        {/* 2-Column Grid for Procedure & Evidence */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* 4. PROCEDURE */}
          <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-900/60 border border-slate-200/70 dark:border-slate-800/80">
            <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 tracking-wider uppercase mb-1">
              PROCEDURE
            </div>
            <div className="text-sm sm:text-base font-semibold text-slate-900 dark:text-white">
              {data.procedure}
            </div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
              Expedited Grant of Licence (30-day timeline)
            </div>
          </div>

          {/* 5. EVIDENCE */}
          <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-900/60 border border-slate-200/70 dark:border-slate-800/80">
            <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 tracking-wider uppercase mb-1">
              EVIDENCE
            </div>
            <div className="text-sm sm:text-base font-semibold text-slate-900 dark:text-white">
              {data.evidenceSource}
            </div>
            <div className="text-xs text-blue-600 dark:text-blue-400 font-medium mt-0.5">
              {data.evidenceItem || "Item 187"}
            </div>
            {data.sourceUrl && (
              <a
                href={data.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-[11px] text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 underline underline-offset-2 mt-1.5 transition-colors"
              >
                <span>View Official BIS Document</span>
                <svg
                  className="w-3 h-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                  />
                </svg>
              </a>
            )}
          </div>
        </div>

        {/* 6. NEXT STEP */}
        <div className="p-4 rounded-xl bg-emerald-50/40 dark:bg-emerald-950/20 border border-emerald-200/70 dark:border-emerald-900/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="text-[11px] font-bold text-emerald-800 dark:text-emerald-400 tracking-wider uppercase mb-0.5">
              RECOMMENDED NEXT ACTION
            </div>
            <div className="text-sm font-semibold text-emerald-950 dark:text-emerald-200">
              {data.nextStep}
            </div>
          </div>

          {onAskFollowUp && (
            <button
              type="button"
              onClick={() =>
                onAskFollowUp(
                  `Explain the step-by-step BIS certification process for a ${data.productIdentified.toLowerCase()} manufacturer under ${data.applicableStandard}.`
                )
              }
              className="inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 shadow-sm transition-all shrink-0 cursor-pointer focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-blue-500"
            >
              <span>Explain Steps in Chat</span>
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
                  d="M14 5l7 7m0 0l-7 7m7-7H3"
                />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Card Footer Actions */}
      <div className="px-5 sm:px-6 py-3.5 border-t border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-[#161C26]/50 flex flex-wrap items-center justify-between gap-2">
        <button
          type="button"
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200/60 dark:hover:bg-slate-800/80 transition-colors cursor-pointer"
        >
          {copied ? (
            <>
              <svg
                className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span className="text-emerald-600 dark:text-emerald-400">
                Copied Summary
              </span>
            </>
          ) : (
            <>
              <svg
                className="w-3.5 h-3.5 text-slate-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
              <span>Copy Assessment</span>
            </>
          )}
        </button>

        {onReset && (
          <button
            type="button"
            onClick={onReset}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/30 transition-colors cursor-pointer"
          >
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
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            <span>Assess Another Product</span>
          </button>
        )}
      </div>
    </div>
  );
}
