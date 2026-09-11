"use client";

import React from "react";
import CitationList from "./CitationList";
import FormattedContent from "./FormattedContent";
import ProductAssessmentCard from "./ProductAssessmentCard";
import Logo from "./Logo";
import { Message } from "../types";
import { Language, translations } from "../i18n";

interface ChatMessageProps {
  message: Message;
  language?: Language;
  onAskFollowUp?: (query: string) => void;
}

export default function ChatMessage({
  message,
  language = "en",
  onAskFollowUp,
}: ChatMessageProps) {
  const isUser = message.role === "user";
  const t = translations[language];

  if (isUser) {
    return (
      <div className="flex justify-end my-3 sm:my-4 animate-in fade-in slide-in-from-bottom-2 duration-200">
        <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-tr-xs px-4 py-2.5 bg-blue-600 text-white text-sm font-normal leading-relaxed shadow-xs">
          <div className="whitespace-pre-wrap break-words">{message.content}</div>
          <div className="text-[10px] text-blue-200/70 text-right mt-1 font-mono">
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        </div>
      </div>
    );
  }

  // Assistant Message: Clean typography, left aligned, subtle original logo avatar
  return (
    <div className="flex items-start gap-3 my-4 sm:my-6 max-w-3xl animate-in fade-in duration-200">
      <div className="shrink-0 mt-0.5">
        <Logo size="sm" />
      </div>

      <div className="flex-1 min-w-0 space-y-3">
        {/* Assistant Header */}
        <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 flex-wrap">
          <span className="font-semibold text-slate-900 dark:text-slate-100">
            {t.appName}
          </span>
          <span className="text-slate-300 dark:text-slate-700">•</span>
          {message.assessment ? (
            <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/50 px-1.5 py-0.2 rounded border border-emerald-200/60 dark:border-emerald-800/60 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              BIS Smart Assessment
            </span>
          ) : message.foundInformation !== false ? (
            <span className="inline-flex items-center gap-1 text-[11px] text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-950/50 px-1.5 py-0.2 rounded border border-blue-200/60 dark:border-blue-800/60">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              {t.chat.groundedBadge}
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[11px] text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/50 px-1.5 py-0.2 rounded border border-amber-200/60 dark:border-amber-900/60">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
              {t.chat.guidanceBadge}
            </span>
          )}
          <time className="text-[10px] font-mono text-slate-400 dark:text-slate-500 ml-auto">
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </time>
        </div>

        {/* If assessment data is attached, display the official Product Assessment Card */}
        {message.assessment ? (
          <ProductAssessmentCard
            data={message.assessment}
            onAskFollowUp={onAskFollowUp}
          />
        ) : (
          <div className="text-slate-800 dark:text-slate-200 leading-relaxed text-sm">
            <FormattedContent content={message.content} />
          </div>
        )}

        {/* Separated Citations Block */}
        {message.citations && message.citations.length > 0 && (
          <CitationList citations={message.citations} language={language} />
        )}
      </div>
    </div>
  );
}
