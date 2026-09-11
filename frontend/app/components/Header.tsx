"use client";

import React from "react";
import Logo from "./Logo";
import ModeSelector from "./ModeSelector";
import LanguageSwitch from "./LanguageSwitch";
import ThemeToggle from "./ThemeToggle";
import { ChatMode } from "../types";
import { Language, translations } from "../i18n";

interface HeaderProps {
  mode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  language: Language;
  onLanguageChange: (lang: Language) => void;
  onNewChat: () => void;
  onOpenAssessment?: () => void;
  disabled?: boolean;
}

export default function Header({
  mode,
  onModeChange,
  language,
  onLanguageChange,
  onNewChat,
  onOpenAssessment,
  disabled = false,
}: HeaderProps) {
  const t = translations[language];

  return (
    <header className="sticky top-0 z-30 w-full border-b border-slate-200/80 dark:border-slate-800/80 bg-white/75 dark:bg-[#0D1117]/80 backdrop-blur-md transition-colors duration-200">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-3">
        {/* LEFT: Original BIS Sahayak Mark + Product Name */}
        <div className="flex items-center gap-2.5 shrink-0">
          <Logo size="md" />
          <span className="font-semibold text-[15px] sm:text-base tracking-tight text-slate-900 dark:text-white">
            {t.appName}
          </span>
        </div>

        {/* RIGHT: Segmented Mode Selector, Smart Assessment, Language Switch, Theme Toggle, New Chat */}
        <div className="flex items-center gap-2 sm:gap-2.5 shrink-0">
          {/* Smart Assessment Quick Button */}
          {onOpenAssessment && (
            <button
              type="button"
              onClick={onOpenAssessment}
              disabled={disabled}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold rounded-lg border border-blue-200/90 dark:border-blue-900/60 bg-blue-50/80 dark:bg-blue-950/40 hover:bg-blue-100 dark:hover:bg-blue-900/60 text-blue-700 dark:text-blue-300 transition-all duration-150 cursor-pointer disabled:opacity-50 shadow-2xs"
            >
              <svg
                className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400"
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
              <span className="hidden sm:inline">Smart Assessment</span>
            </button>
          )}

          {/* Segmented Mode Selector: Consumer | Industry */}
          <ModeSelector
            mode={mode}
            onModeChange={onModeChange}
            disabled={disabled}
            consumerLabel={t.modes.consumer}
            industryLabel={t.modes.industry}
          />

          {/* Language Switch: English | हिन्दी */}
          <LanguageSwitch
            currentLanguage={language}
            onLanguageChange={onLanguageChange}
            disabled={disabled}
          />

          {/* Light / Dark Theme Toggle */}
          <ThemeToggle
            labelLight={t.header.lightMode}
            labelDark={t.header.darkMode}
          />

          {/* New Chat Button */}
          <button
            type="button"
            onClick={onNewChat}
            disabled={disabled}
            aria-label={t.header.newChat}
            title={t.header.newChat}
            className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium rounded-lg border border-slate-200/90 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-all duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shadow-2xs"
          >
            <svg
              className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
            <span className="hidden sm:inline">{t.header.newChat}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
