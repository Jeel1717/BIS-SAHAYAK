"use client";

import React from "react";

interface FormattedContentProps {
  content: string;
}

function renderInline(text: string): React.ReactNode[] {
  // Regex to match:
  // 1. Markdown link: [text](url)
  // 2. Bold text: **text**
  // 3. Inline code: `code`
  // 4. Citation badge: [1], [2], etc.
  // 5. Indian Standard badge: IS 1234, IS 14543:2004, etc.
  const tokenRegex = /(\[[^\]]+\]\(https?:\/\/[^\)]+\)|\*\*[^*]+\*\*|`[^`]+`|\[\d+\]|IS\s+\d+(?::\d+)?(?:-[A-Za-z0-9]+)?)/g;
  const parts = text.split(tokenRegex);

  return parts.map((part, idx) => {
    if (!part) return null;

    // Markdown link: [text](url)
    const linkMatch = part.match(/^\[([^\]]+)\]\((https?:\/\/[^\)]+)\)$/);
    if (linkMatch) {
      return (
        <a
          key={idx}
          href={linkMatch[2]}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 dark:text-blue-400 underline underline-offset-2 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
        >
          {linkMatch[1]}
        </a>
      );
    }

    // Bold text: **text**
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return (
        <strong key={idx} className="font-semibold text-slate-900 dark:text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }

    // Inline code: `code`
    if (part.startsWith("`") && part.endsWith("`") && part.length > 2) {
      return (
        <code
          key={idx}
          className="px-1.5 py-0.5 rounded text-xs font-mono bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200/80 dark:border-slate-700"
        >
          {part.slice(1, -1)}
        </code>
      );
    }

    // Inline citation badge [1], [2], etc.
    if (/^\[\d+\]$/.test(part)) {
      return (
        <span
          key={idx}
          className="inline-flex items-center justify-center px-1.5 py-0.5 mx-0.5 rounded text-[10px] font-semibold bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200/60 dark:border-blue-800/60 align-baseline select-none"
          title={`Official BIS Source ${part}`}
        >
          {part}
        </span>
      );
    }

    // Indian Standard identifier, e.g. IS 14543
    if (/^IS\s+\d+/.test(part)) {
      return (
        <span
          key={idx}
          className="inline-flex items-center px-1.5 py-0.2 mx-0.5 rounded font-mono text-[11px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200/80 dark:border-slate-700"
        >
          {part}
        </span>
      );
    }

    return <React.Fragment key={idx}>{part}</React.Fragment>;
  });
}

export default function FormattedContent({ content }: FormattedContentProps) {
  if (!content) return null;

  const lines = content.split("\n");
  const blocks: React.ReactNode[] = [];
  let currentList: { type: "bullet" | "number"; items: string[] } | null = null;
  let currentQuote: string[] = [];

  const flushQuote = () => {
    if (currentQuote.length === 0) return;
    const quoteText = currentQuote.join(" ");
    blocks.push(
      <blockquote
        key={`quote-${blocks.length}`}
        className="my-2.5 pl-3 py-1.5 border-l-2 border-blue-500/70 dark:border-blue-400/70 bg-blue-50/40 dark:bg-blue-950/30 rounded-r-md text-xs sm:text-sm text-slate-700 dark:text-slate-300"
      >
        {renderInline(quoteText)}
      </blockquote>
    );
    currentQuote = [];
  };

  const flushList = () => {
    if (!currentList) return;

    if (currentList.type === "bullet") {
      blocks.push(
        <ul key={`list-${blocks.length}`} className="my-2 space-y-1 pl-0.5">
          {currentList.items.map((item, i) => (
            <li key={i} className="flex items-start gap-2.5 text-sm leading-relaxed text-slate-700 dark:text-slate-200">
              <span className="shrink-0 w-1.5 h-1.5 rounded-full bg-blue-500/80 dark:bg-blue-400/80 mt-2" />
              <span className="flex-1">{renderInline(item)}</span>
            </li>
          ))}
        </ul>
      );
    } else {
      blocks.push(
        <ol key={`list-${blocks.length}`} className="my-2.5 space-y-1.5 pl-0.5">
          {currentList.items.map((item, i) => (
            <li key={i} className="flex items-start gap-2.5 text-sm leading-relaxed text-slate-700 dark:text-slate-200">
              <span className="shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-[11px] font-semibold border border-slate-200 dark:border-slate-700 mt-0.5 select-none">
                {i + 1}
              </span>
              <span className="flex-1">{renderInline(item)}</span>
            </li>
          ))}
        </ol>
      );
    }
    currentList = null;
  };

  const flushAll = () => {
    flushList();
    flushQuote();
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (!line) {
      flushAll();
      continue;
    }

    // Blockquote: > text
    if (line.startsWith("> ")) {
      flushList();
      currentQuote.push(line.replace(/^>\s*/, ""));
      continue;
    } else if (currentQuote.length > 0) {
      flushQuote();
    }

    // Section Headings: # or ##
    if (line.startsWith("# ") || line.startsWith("## ")) {
      flushAll();
      const headingText = line.replace(/^#+\s+/, "");
      blocks.push(
        <h2
          key={`h2-${i}`}
          className="text-sm sm:text-base font-semibold text-slate-900 dark:text-white mt-4 mb-1.5 tracking-tight flex items-center gap-1.5"
        >
          {renderInline(headingText)}
        </h2>
      );
      continue;
    }

    // Sub-headings: ### or ####
    if (line.startsWith("### ") || line.startsWith("#### ")) {
      flushAll();
      const headingText = line.replace(/^#+\s+/, "");
      blocks.push(
        <h3
          key={`h3-${i}`}
          className="text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-100 mt-3 mb-1"
        >
          {renderInline(headingText)}
        </h3>
      );
      continue;
    }

    // Numbered item: 1. or 1)
    const numMatch = line.match(/^(\d+)[.)]\s+(.+)$/);
    if (numMatch) {
      flushQuote();
      if (!currentList || currentList.type !== "number") {
        flushList();
        currentList = { type: "number", items: [] };
      }
      currentList.items.push(numMatch[2]);
      continue;
    }

    // Bullet item: - or * or •
    const bulletMatch = line.match(/^[-*•]\s+(.+)$/);
    if (bulletMatch) {
      flushQuote();
      if (!currentList || currentList.type !== "bullet") {
        flushList();
        currentList = { type: "bullet", items: [] };
      }
      currentList.items.push(bulletMatch[1]);
      continue;
    }

    // Standalone bold line acting as a mini header
    if (line.startsWith("**") && line.endsWith("**") && line.length < 70 && !line.includes(". ")) {
      flushAll();
      blocks.push(
        <h4
          key={`bold-h-${i}`}
          className="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white mt-2.5 mb-1"
        >
          {line.slice(2, -2)}
        </h4>
      );
      continue;
    }

    // Standard Paragraph
    flushAll();
    blocks.push(
      <p
        key={`p-${i}`}
        className="text-sm leading-relaxed text-slate-700 dark:text-slate-200 my-1.5"
      >
        {renderInline(line)}
      </p>
    );
  }

  flushAll();

  return <div className="space-y-1">{blocks}</div>;
}
