"use client";

import React from "react";

export default function BackgroundGraphics() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 overflow-hidden select-none"
    >
      {/* Layer 1: Base Technical Precision Grid */}
      <div className="absolute inset-0 bg-tech-grid opacity-80" />

      {/* Layer 2: Subtle Radial Ambient Glows */}
      {/* Central glow behind assistant */}
      <div
        className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] rounded-full blur-3xl opacity-50 dark:opacity-40 transition-opacity duration-500"
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(59, 130, 246, 0.12), rgba(99, 102, 241, 0.05) 50%, transparent 80%)",
        }}
      />

      {/* Soft secondary top glow */}
      <div
        className="absolute -top-32 right-1/4 w-[500px] h-[400px] rounded-full blur-3xl opacity-30 dark:opacity-25"
        style={{
          background:
            "radial-gradient(circle at center, rgba(14, 165, 233, 0.08), transparent 70%)",
        }}
      />

      {/* Soft bottom-left ambient tone */}
      <div
        className="absolute bottom-10 left-1/10 w-[450px] h-[350px] rounded-full blur-3xl opacity-25 dark:opacity-20"
        style={{
          background:
            "radial-gradient(circle at center, rgba(99, 102, 241, 0.06), transparent 70%)",
        }}
      />

      {/* Layer 3: Precision Standards Geometry (SVG technical lines, calibration arcs, crosshairs) */}
      <svg
        className="absolute inset-0 w-full h-full text-slate-400/20 dark:text-slate-600/20"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Subtle dash patterns */}
          <pattern
            id="subtle-dots"
            x="0"
            y="0"
            width="64"
            height="64"
            patternUnits="userSpaceOnUse"
          >
            <circle cx="2" cy="2" r="1" fill="currentColor" opacity="0.35" />
          </pattern>
        </defs>

        {/* Global dot matrix accents */}
        <rect width="100%" height="100%" fill="url(#subtle-dots)" opacity="0.5" />

        {/* Central standards calibration concentric arcs behind welcome zone */}
        <g className="opacity-40 dark:opacity-30">
          {/* Outer Calibration Ring */}
          <circle
            cx="50%"
            cy="36%"
            r="320"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            strokeDasharray="4 8"
          />

          {/* Inner Calibration Ring */}
          <circle
            cx="50%"
            cy="36%"
            r="190"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            strokeDasharray="2 12"
          />

          {/* Core Alignment Ring */}
          <circle
            cx="50%"
            cy="36%"
            r="90"
            fill="none"
            stroke="currentColor"
            strokeWidth="0.8"
            opacity="0.6"
          />

          {/* Horizontal and vertical alignment lines */}
          <line
            x1="calc(50% - 350px)"
            y1="36%"
            x2="calc(50% + 350px)"
            y2="36%"
            stroke="currentColor"
            strokeWidth="0.75"
            strokeDasharray="6 14"
            opacity="0.3"
          />
          <line
            x1="50%"
            y1="calc(36% - 240px)"
            x2="50%"
            y2="calc(36% + 240px)"
            stroke="currentColor"
            strokeWidth="0.75"
            strokeDasharray="6 14"
            opacity="0.3"
          />
        </g>

        {/* Precision Crosshair Marks in corners */}
        {/* Top-left crosshair */}
        <g className="opacity-30 dark:opacity-20" transform="translate(48, 96)">
          <line x1="-8" y1="0" x2="8" y2="0" stroke="currentColor" strokeWidth="1.2" />
          <line x1="0" y1="-8" x2="0" y2="8" stroke="currentColor" strokeWidth="1.2" />
          <circle cx="0" cy="0" r="3" fill="none" stroke="currentColor" strokeWidth="0.8" />
        </g>

        {/* Top-right crosshair */}
        <g className="opacity-30 dark:opacity-20" transform="translate(calc(100% - 48px), 96)">
          <line x1="-8" y1="0" x2="8" y2="0" stroke="currentColor" strokeWidth="1.2" />
          <line x1="0" y1="-8" x2="0" y2="8" stroke="currentColor" strokeWidth="1.2" />
          <circle cx="0" cy="0" r="3" fill="none" stroke="currentColor" strokeWidth="0.8" />
        </g>

        {/* Bottom-left technical angle marker */}
        <g className="opacity-25 dark:opacity-15" transform="translate(64, calc(100% - 120px))">
          <path d="M0 24 L0 0 L24 0" fill="none" stroke="currentColor" strokeWidth="1.2" />
          <text x="6" y="16" fill="currentColor" fontSize="9" fontFamily="monospace" opacity="0.6">
            IS/SEC
          </text>
        </g>

        {/* Bottom-right technical angle marker */}
        <g className="opacity-25 dark:opacity-15" transform="translate(calc(100% - 88px), calc(100% - 120px))">
          <path d="M24 24 L24 0 L0 0" fill="none" stroke="currentColor" strokeWidth="1.2" />
          <text x="-18" y="16" fill="currentColor" fontSize="9" fontFamily="monospace" opacity="0.6">
            VERIFIED
          </text>
        </g>
      </svg>
    </div>
  );
}
