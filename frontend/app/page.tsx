"use client";

import React, { useState, useRef, useEffect } from "react";
import Header from "./components/Header";
import BackgroundGraphics from "./components/BackgroundGraphics";
import WelcomeScreen from "./components/WelcomeScreen";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import LoadingIndicator from "./components/LoadingIndicator";
import SmartAssessmentModal from "./components/SmartAssessmentModal";
import { ChatMode, Message, ChatApiResponse, AssessmentData } from "./types";
import { Language, translations } from "./i18n";
import { parseAssessmentResponse } from "./utils/assessmentParser";

const rawApiUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";
const API_URL = rawApiUrl.replace(/\/+$/, "");

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [mode, setMode] = useState<ChatMode>("consumer");
  const [language, setLanguage] = useState<Language>("en");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastQuery, setLastQuery] = useState<string | null>(null);

  // BIS Smart Assessment state
  const [assessmentResult, setAssessmentResult] = useState<AssessmentData | null>(null);
  const [isAssessmentLoading, setIsAssessmentLoading] = useState(false);
  const [showAssessmentModal, setShowAssessmentModal] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const t = translations[language];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(null);
    setErrorMessage(null);
    setLastQuery(null);
    setAssessmentResult(null);
    setShowAssessmentModal(false);
  };

  // ── 1. Standard Chat Message Handler ───────────────────────────────────────
  const handleSendMessage = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    setErrorMessage(null);
    setLastQuery(trimmed);

    // 1. Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmed,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 2. Call backend /api/v1/chat
      const response = await fetch(`${API_URL}/api/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmed,
          session_id: sessionId,
          mode: mode,
        }),
      });

      if (!response.ok) {
        if (response.status === 503) {
          throw new Error(t.chat.errorDemand);
        } else {
          throw new Error(t.chat.errorConnect);
        }
      }

      const data: ChatApiResponse = await response.json();

      if (data.session_id) {
        setSessionId(data.session_id);
      }

      // 3. Add assistant response
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.answer,
        citations: data.citations || [],
        foundInformation: data.found_information,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Chat error:", err);
      const msg =
        err instanceof Error ? err.message : t.chat.errorConnect;
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  // ── 2. BIS Smart Assessment Handler ────────────────────────────────────────
  const handleAnalyzeProduct = async (productDescription: string) => {
    const trimmed = productDescription.trim();
    if (!trimmed || isAssessmentLoading) return;

    setIsAssessmentLoading(true);
    setErrorMessage(null);

    // Prompt as specified for jury evaluation
    const assessmentPrompt = `Analyze this product for BIS requirements using ONLY the retrieved official BIS evidence.

Product: ${trimmed}

Return:
1. Product identified
2. Applicable Indian Standard(s)
3. BIS certification scheme/pathway
4. Procedure, if explicitly supported
5. Evidence/source
6. Recommended next action

Do not invent facts. If evidence is insufficient, say so.`;

    try {
      const response = await fetch(`${API_URL}/api/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: assessmentPrompt,
          session_id: sessionId,
          mode: "industry", // Industry mode targets conformity assessment & standards
        }),
      });

      if (!response.ok) {
        if (response.status === 503) {
          throw new Error(t.chat.errorDemand);
        } else {
          throw new Error(t.chat.errorConnect);
        }
      }

      const data: ChatApiResponse = await response.json();

      if (data.session_id) {
        setSessionId(data.session_id);
      }

      const parsedAssessment = parseAssessmentResponse(data, trimmed);
      setAssessmentResult(parsedAssessment);
    } catch (err) {
      console.error("Assessment error:", err);
      const msg =
        err instanceof Error ? err.message : t.chat.errorConnect;
      setErrorMessage(msg);
    } finally {
      setIsAssessmentLoading(false);
    }
  };

  // ── 3. Follow-up from Assessment to Chat ───────────────────────────────────
  const handleAskFollowUp = (queryText: string) => {
    if (assessmentResult && messages.length === 0) {
      // First persist the structured assessment report in conversation
      const assessmentMsg: Message = {
        id: `assessment-${Date.now()}`,
        role: "assistant",
        content: assessmentResult.rawAnswer,
        citations: [
          {
            number: 1,
            title: assessmentResult.evidenceSource,
            source_url: assessmentResult.sourceUrl || "https://www.bis.gov.in",
            clause_number: null,
            page_number: null,
          },
        ],
        foundInformation: true,
        timestamp: new Date(),
        assessment: assessmentResult,
      };
      setMessages([assessmentMsg]);
      setAssessmentResult(null);
    }
    handleSendMessage(queryText);
  };

  return (
    <div className="relative flex flex-col min-h-screen bg-[var(--background)] text-[var(--foreground)] overflow-x-hidden antialiased transition-colors duration-250">
      {/* Sophisticated Ambient Background Graphics (CSS + SVG) */}
      <BackgroundGraphics />

      {/* Header */}
      <Header
        mode={mode}
        onModeChange={setMode}
        language={language}
        onLanguageChange={setLanguage}
        onNewChat={handleNewChat}
        onOpenAssessment={() => setShowAssessmentModal(true)}
        disabled={isLoading || isAssessmentLoading}
      />

      {/* Smart Assessment Modal (Available from Header anywhere) */}
      <SmartAssessmentModal
        isOpen={showAssessmentModal}
        onClose={() => setShowAssessmentModal(false)}
        onAnalyze={handleAnalyzeProduct}
        isLoading={isAssessmentLoading}
        assessmentResult={assessmentResult}
        onAskFollowUp={handleAskFollowUp}
        onReset={() => setAssessmentResult(null)}
      />

      {/* Main Conversation Area */}
      <main className="relative z-10 flex-1 flex flex-col max-w-3xl w-full mx-auto px-4 sm:px-6">
        {/* Error Banner */}
        {errorMessage && (
          <div
            role="alert"
            className="my-3 p-3 rounded-xl bg-red-50/90 dark:bg-red-950/40 border border-red-200/80 dark:border-red-900/60 text-red-700 dark:text-red-300 text-xs flex items-center justify-between gap-3 shadow-2xs animate-in fade-in"
          >
            <span className="truncate flex-1">{errorMessage}</span>
            <div className="flex items-center gap-2 shrink-0">
              {lastQuery && (
                <button
                  type="button"
                  onClick={() => handleSendMessage(lastQuery)}
                  className="px-2.5 py-1 rounded-lg bg-red-100 dark:bg-red-900/60 hover:bg-red-200 dark:hover:bg-red-800 text-red-800 dark:text-red-200 font-medium text-[11px] cursor-pointer transition-colors focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-red-500"
                >
                  {t.chat.retry}
                </button>
              )}
              <button
                type="button"
                onClick={() => setErrorMessage(null)}
                aria-label="Dismiss error"
                className="p-1 rounded text-red-500 hover:text-red-700 dark:hover:text-red-200 font-bold cursor-pointer text-sm leading-none focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-red-500"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Content: Welcome Hero with Smart Assessment Card or Active Chat Stream */}
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <WelcomeScreen
              mode={mode}
              language={language}
              onSelectPrompt={handleSendMessage}
              onAnalyzeProduct={handleAnalyzeProduct}
              isAssessmentLoading={isAssessmentLoading}
              assessmentResult={assessmentResult}
              onAskFollowUp={handleAskFollowUp}
              onResetAssessment={() => setAssessmentResult(null)}
              disabled={isLoading || isAssessmentLoading}
            />
          </div>
        ) : (
          <div className="flex-1 py-4 sm:py-6 space-y-1">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                language={language}
                onAskFollowUp={handleAskFollowUp}
              />
            ))}

            {isLoading && <LoadingIndicator language={language} />}

            <div ref={messagesEndRef} aria-hidden="true" />
          </div>
        )}
      </main>

      {/* Floating Bottom Input Bar */}
      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={isLoading || isAssessmentLoading}
        language={language}
      />
    </div>
  );
}
