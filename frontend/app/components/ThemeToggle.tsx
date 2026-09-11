"use client";

import React, { useEffect, useSyncExternalStore } from "react";

interface ThemeToggleProps {
  labelLight?: string;
  labelDark?: string;
}

const emptySubscribe = () => () => {};

function useIsClient(): boolean {
  return useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false
  );
}

function getSnapshot(): "light" | "dark" {
  if (typeof window === "undefined") return "light";
  const saved = localStorage.getItem("bis-sahayak-theme") as "light" | "dark" | null;
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function getServerSnapshot(): "light" | "dark" {
  return "light";
}

function subscribe(callback: () => void): () => void {
  window.addEventListener("storage", callback);
  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  mediaQuery.addEventListener("change", callback);

  return () => {
    window.removeEventListener("storage", callback);
    mediaQuery.removeEventListener("change", callback);
  };
}

export default function ThemeToggle({
  labelLight = "Light Mode",
  labelDark = "Dark Mode",
}: ThemeToggleProps) {
  const isClient = useIsClient();
  const theme = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  useEffect(() => {
    if (isClient) {
      document.documentElement.classList.toggle("dark", theme === "dark");
    }
  }, [theme, isClient]);

  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    localStorage.setItem("bis-sahayak-theme", next);
    document.documentElement.classList.toggle("dark", next === "dark");
    window.dispatchEvent(new Event("storage"));
  };

  if (!isClient) {
    return (
      <div className="w-8 h-8 rounded-lg border border-slate-200/90 dark:border-slate-800 bg-slate-100/50 dark:bg-slate-900/50" />
    );
  }

  const isDark = theme === "dark";

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={isDark ? labelLight : labelDark}
      title={isDark ? labelLight : labelDark}
      className="flex items-center justify-center w-8 h-8 rounded-lg border border-slate-200/90 dark:border-slate-800 bg-slate-100/70 dark:bg-slate-900/60 hover:bg-white dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-all duration-150 cursor-pointer shadow-2xs focus-visible:ring-2 focus-visible:ring-blue-500"
    >
      {isDark ? (
        <svg
          className="w-3.5 h-3.5 text-amber-400 transition-transform duration-200 hover:rotate-45"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
      ) : (
        <svg
          className="w-3.5 h-3.5 text-slate-700 transition-transform duration-200 hover:-rotate-12"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>
      )}
    </button>
  );
}
