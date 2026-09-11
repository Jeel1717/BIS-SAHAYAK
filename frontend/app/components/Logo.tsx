"use client";

import React from "react";

interface LogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  showWordmark?: boolean;
  wordmarkClassName?: string;
}

/**
 * Original BIS Sahayak visual mark:
 * Synthesizes standards (precision calibration calipers & geometric boundary),
 * intelligence (flowing technical form), and verification (confident verification glyph).
 * Independent original design.
 */
export default function Logo({
  size = "md",
  className = "",
  showWordmark = false,
  wordmarkClassName = "",
}: LogoProps) {
  const sizeMap = {
    sm: "w-6 h-6",
    md: "w-8 h-8",
    lg: "w-11 h-11",
    xl: "w-14 h-14",
  };

  const containerSize = sizeMap[size] || sizeMap.md;

  return (
    <div className={`inline-flex items-center gap-2.5 ${className}`}>
      <div
        className={`relative flex items-center justify-center shrink-0 ${containerSize} rounded-xl bg-gradient-to-br from-slate-900 via-slate-950 to-blue-950 dark:from-slate-900 dark:via-blue-950 dark:to-indigo-950 p-1.5 shadow-sm shadow-blue-950/20 ring-1 ring-black/5 dark:ring-white/10 transition-transform duration-200`}
        aria-hidden="true"
      >
        <svg
          viewBox="0 0 36 36"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full"
        >
          <defs>
            <linearGradient
              id="bsOuterGrad"
              x1="3"
              y1="3"
              x2="33"
              y2="33"
              gradientUnits="userSpaceOnUse"
            >
              <stop offset="0%" stopColor="#60A5FA" />
              <stop offset="50%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#4F46E5" />
            </linearGradient>

            <linearGradient
              id="bsCheckGrad"
              x1="11"
              y1="16"
              x2="25"
              y2="26"
              gradientUnits="userSpaceOnUse"
            >
              <stop offset="0%" stopColor="#38BDF8" />
              <stop offset="100%" stopColor="#60A5FA" />
            </linearGradient>

            <linearGradient
              id="goldNodeGrad"
              x1="0"
              y1="0"
              x2="4"
              y2="4"
              gradientUnits="userSpaceOnUse"
            >
              <stop offset="0%" stopColor="#FBBF24" />
              <stop offset="100%" stopColor="#F59E0B" />
            </linearGradient>
          </defs>

          {/* Outer Precision Standards Frame: Geometric Beveled Hexagon */}
          <path
            d="M18 3.5L31.5 11.3V26.7L18 34.5L4.5 26.7V11.3L18 3.5Z"
            stroke="url(#bsOuterGrad)"
            strokeWidth="2"
            strokeLinejoin="round"
            className="opacity-90"
          />

          {/* Technical Calibration Notches on Cardinal Axes */}
          <line x1="18" y1="5.5" x2="18" y2="8.5" stroke="#93C5FD" strokeWidth="1.5" strokeLinecap="round" opacity="0.7" />
          <line x1="18" y1="29.5" x2="18" y2="32.5" stroke="#93C5FD" strokeWidth="1.5" strokeLinecap="round" opacity="0.7" />
          <line x1="6.5" y1="19" x2="9.5" y2="19" stroke="#93C5FD" strokeWidth="1.5" strokeLinecap="round" opacity="0.7" />
          <line x1="26.5" y1="19" x2="29.5" y2="19" stroke="#93C5FD" strokeWidth="1.5" strokeLinecap="round" opacity="0.7" />

          {/* Central Stylized "S" / Precision Verification Check Glyph */}
          <path
            d="M12 18.5L16.5 23L24.5 13.5"
            stroke="url(#bsCheckGrad)"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Precision Verification Focal Node */}
          <circle cx="24.5" cy="13.5" r="1.5" fill="url(#goldNodeGrad)" />
        </svg>
      </div>

      {showWordmark && (
        <span
          className={`font-semibold tracking-tight text-slate-900 dark:text-white ${wordmarkClassName}`}
        >
          BIS Sahayak
        </span>
      )}
    </div>
  );
}
