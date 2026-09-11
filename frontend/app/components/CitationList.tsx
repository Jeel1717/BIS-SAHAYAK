"use client";

import React, { useState } from "react";
import { Citation } from "../types";
import { Language, translations } from "../i18n";

interface CitationListProps {
  citations: Citation[];
  language?: Language;
}

export default function CitationList({
  citations,
  language = "en",
}: CitationListProps) {
  // Collapsed by default for a compact, clean look as per Chapter 15 guidelines
  const [isOpen, setIsOpen] = useState(false);
  const t = translations[language];

  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 pt-2.5 border-t border-slate-200/60 dark:border-slate-800/80">
      {/* Header: Compact Sources · N Toggle */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="inline-flex items-center gap-2 px-2 py-1 -ml-2 rounded-lg text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100/80 dark:hover:bg-slate-800/60 transition-colors cursor-pointer group focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-blue-500"
          aria-expanded={isOpen}
          aria-label={`${t.chat.sourcesTitle}: ${citations.length}`}
        >
          <span className="font-semibold text-slate-700 dark:text-slate-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
            {t.chat.sourcesTitle}
          </span>
          <span className="inline-flex items-center justify-center px-1.5 py-0.2 rounded-full text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700">
            {citations.length}
          </span>
          <svg
            className={`w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-transform duration-200 ${
              isOpen ? "rotate-180" : ""
            }`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <span className="text-[11px] text-slate-400 dark:text-slate-500 hidden sm:inline">
          {t.chat.verifySource}
        </span>
      </div>

      {/* Clean Compact Cards Grid */}
      {isOpen && (
        <div className="mt-2.5 flex flex-col sm:flex-row flex-wrap gap-2 animate-in fade-in slide-in-from-top-1 duration-150">
          {citations.map((citation) => (
            <a
              key={citation.number}
              href={citation.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 min-w-[240px] max-w-full flex items-start gap-2.5 p-2.5 rounded-xl bg-slate-50/90 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80 hover:border-blue-400/80 dark:hover:border-blue-500/70 hover:bg-white dark:hover:bg-slate-900 transition-all duration-150 group text-left shadow-2xs focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-blue-500"
              title={`Open official document: ${citation.title}`}
            >
              {/* Citation Badge [1] */}
              <span className="shrink-0 flex items-center justify-center w-5 h-5 rounded-md bg-blue-50 dark:bg-blue-950/80 text-blue-600 dark:text-blue-400 font-semibold text-[11px] border border-blue-200/60 dark:border-blue-800/60 mt-0.5 select-none">
                [{citation.number}]
              </span>

              {/* Title & Official Badges */}
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-slate-800 dark:text-slate-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-1 leading-snug">
                  {citation.title}
                </p>
                <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                  {/* Verified Official Domain Badge */}
                  <span className="inline-flex items-center gap-1 text-[10px] font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 px-1.5 py-0.2 rounded border border-emerald-200/60 dark:border-emerald-900/50">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    bis.gov.in
                  </span>

                  {/* Clause / Section if present */}
                  {citation.clause_number && (
                    <span className="inline-flex items-center text-[10px] font-medium text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.2 rounded border border-slate-200/60 dark:border-slate-700">
                      {citation.clause_number}
                    </span>
                  )}
                </div>
              </div>

              {/* External Link Icon */}
              <svg
                className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-500 shrink-0 transition-colors mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
