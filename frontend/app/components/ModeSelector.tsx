"use client";

import React from "react";
import { ChatMode } from "../types";

interface ModeSelectorProps {
  mode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  disabled?: boolean;
  consumerLabel?: string;
  industryLabel?: string;
}

export default function ModeSelector({
  mode,
  onModeChange,
  disabled = false,
  consumerLabel = "Consumer",
  industryLabel = "Industry",
}: ModeSelectorProps) {
  return (
    <div
      role="tablist"
      aria-label="Target perspective"
      className="inline-flex items-center p-0.5 rounded-lg border border-slate-200/90 dark:border-slate-800 bg-slate-100/70 dark:bg-slate-900/60 text-xs shadow-2xs backdrop-blur-xs"
    >
      <button
        type="button"
        role="tab"
        aria-selected={mode === "consumer"}
        onClick={() => onModeChange("consumer")}
        disabled={disabled}
        className={`px-2.5 py-1 rounded-[6px] font-medium transition-all duration-150 cursor-pointer select-none ${
          mode === "consumer"
            ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs font-semibold"
            : "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        {consumerLabel}
      </button>

      <button
        type="button"
        role="tab"
        aria-selected={mode === "industry"}
        onClick={() => onModeChange("industry")}
        disabled={disabled}
        className={`px-2.5 py-1 rounded-[6px] font-medium transition-all duration-150 cursor-pointer select-none ${
          mode === "industry"
            ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs font-semibold"
            : "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        {industryLabel}
      </button>
    </div>
  );
}
