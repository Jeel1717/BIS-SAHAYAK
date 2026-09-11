"use client";

import React, { useState, useEffect } from "react";
import Logo from "./Logo";
import { Language, translations } from "../i18n";

interface LoadingIndicatorProps {
  language?: Language;
}

export default function LoadingIndicator({
  language = "en",
}: LoadingIndicatorProps) {
  const t = translations[language];
  const [phase, setPhase] = useState<"searching" | "synthesizing">("searching");

  useEffect(() => {
    const timer = setTimeout(() => {
      setPhase("synthesizing");
    }, 2600);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div
      className="flex items-start gap-3 my-4 sm:my-6 max-w-3xl animate-in fade-in duration-200"
      role="status"
      aria-live="polite"
      aria-label={phase === "searching" ? t.chat.searching : t.chat.synthesizing}
    >
      <div className="shrink-0 mt-0.5">
        <Logo size="sm" />
      </div>

      <div className="flex items-center gap-2.5 text-xs font-medium text-slate-500 dark:text-slate-400 py-1">
        {/* Subtle breathing dot with reduced-motion support */}
        <span className="relative flex h-2 w-2 items-center justify-center">
          <span className="motion-reduce:hidden animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-60"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-600 dark:bg-blue-400"></span>
        </span>

        <span className="transition-opacity duration-300 text-slate-600 dark:text-slate-300">
          {phase === "searching" ? t.chat.searching : t.chat.synthesizing}
        </span>
      </div>
    </div>
  );
}
