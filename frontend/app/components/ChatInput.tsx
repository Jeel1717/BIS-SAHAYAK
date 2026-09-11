"use client";

import React, { useState, useRef, useEffect } from "react";
import { Language, translations } from "../i18n";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  language?: Language;
}

export default function ChatInput({
  onSendMessage,
  disabled = false,
  language = "en",
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const t = translations[language];

  // Auto-grow textarea height up to 160px
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        160
      )}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSendMessage(trimmed);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="sticky bottom-0 z-20 w-full bg-gradient-to-t from-[var(--background)] via-[var(--background)] to-transparent pt-4 pb-4 px-4 sm:px-6">
      <div className="max-w-3xl mx-auto w-full">
        {/* Rounded Premium Input Box */}
        <form
          onSubmit={handleSubmit}
          className="relative flex items-end gap-2 bg-white/95 dark:bg-[#161B22]/95 backdrop-blur-md rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-sm shadow-slate-200/50 dark:shadow-black/20 focus-within:border-blue-500/80 focus-within:ring-2 focus-within:ring-blue-500/15 transition-all p-1.5 sm:p-2"
        >
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            maxLength={2000}
            aria-label={t.chat.inputPlaceholder}
            placeholder={t.chat.inputPlaceholder}
            className="flex-1 max-h-40 min-h-[44px] py-2 px-3 bg-transparent text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-hidden resize-none leading-relaxed"
          />

          <div className="flex items-center gap-1.5 pb-1 pr-1 shrink-0">
            {input.length > 1500 && (
              <span className="text-[10px] text-slate-400 font-mono">
                {input.length}/2000
              </span>
            )}

            {/* Send Button with clean upward arrow ↑ */}
            <button
              type="submit"
              disabled={disabled || !input.trim()}
              aria-label={t.chat.sendTooltip}
              title={t.chat.sendTooltip}
              className="flex items-center justify-center w-8 h-8 sm:w-8.5 sm:h-8.5 rounded-xl bg-blue-600 hover:bg-blue-700 active:scale-95 disabled:bg-slate-100 dark:disabled:bg-slate-800 text-white disabled:text-slate-300 dark:disabled:text-slate-600 transition-all duration-150 cursor-pointer disabled:cursor-not-allowed shadow-xs focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-blue-500"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2.2"
                  d="M5 10l7-7m0 0l7 7m-7-7v18"
                />
              </svg>
            </button>
          </div>
        </form>

        {/* Minimal Disclaimers */}
        <p className="mt-2 text-[11px] text-center text-slate-400 dark:text-slate-500 leading-tight">
          {t.chat.disclaimer}
        </p>
      </div>
    </div>
  );
}
