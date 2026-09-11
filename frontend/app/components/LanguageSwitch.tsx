"use client";

import React from "react";
import { Language } from "../i18n";

interface LanguageSwitchProps {
  currentLanguage: Language;
  onLanguageChange: (lang: Language) => void;
  disabled?: boolean;
}

export default function LanguageSwitch({
  currentLanguage,
  onLanguageChange,
  disabled = false,
}: LanguageSwitchProps) {
  return (
    <div
      role="group"
      aria-label="Language selection"
      className="inline-flex items-center p-0.5 rounded-lg border border-slate-200/90 dark:border-slate-800 bg-slate-100/70 dark:bg-slate-900/60 text-xs shadow-2xs backdrop-blur-xs"
    >
      <button
        type="button"
        onClick={() => onLanguageChange("en")}
        disabled={disabled}
        aria-pressed={currentLanguage === "en"}
        className={`px-2 py-1 rounded-[6px] font-medium transition-all duration-150 cursor-pointer select-none ${
          currentLanguage === "en"
            ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs font-semibold"
            : "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        English
      </button>

      <button
        type="button"
        onClick={() => onLanguageChange("hi")}
        disabled={disabled}
        aria-pressed={currentLanguage === "hi"}
        className={`px-2 py-1 rounded-[6px] font-medium transition-all duration-150 cursor-pointer select-none ${
          currentLanguage === "hi"
            ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs font-semibold"
            : "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        हिन्दी
      </button>
    </div>
  );
}
