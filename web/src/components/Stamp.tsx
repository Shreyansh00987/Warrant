"use client";

import React from "react";
import { WarrantStatus, ScopeResult } from "@/types";

interface StampProps {
  status: WarrantStatus | ScopeResult | "VERIFIED";
  approver?: string;
  date?: string;
  className?: string;
  animated?: boolean;
}

export function Stamp({
  status,
  approver,
  date,
  className = "",
  animated = true,
}: StampProps) {
  let label = "PENDING";
  let colorClass = "text-ink-muted border-ink-muted/40";
  let animClass = "";
  let rotateStyle = "rotate(0deg)";

  if (status === "APPROVED_MERGE" || status === "APPROVED_PLAN") {
    label = "APPROVED";
    colorClass = "text-oxblood border-oxblood";
    animClass = animated ? "animate-stamp" : "";
    rotateStyle = "rotate(-2deg)";
  } else if (status === "OUT_OF_SCOPE" || status === "SCOPE_VIOLATION") {
    label = "OUT OF SCOPE";
    colorClass = "text-oxblood border-oxblood";
    animClass = animated ? "animate-stamp-red" : "";
    rotateStyle = "rotate(2deg)";
  } else if (status === "BLOCKED") {
    label = "BLOCKED";
    colorClass = "text-oxblood border-oxblood";
    animClass = animated ? "animate-stamp" : "";
    rotateStyle = "rotate(-1.5deg)";
  } else if (status === "VERIFIED") {
    label = "VERIFIED";
    colorClass = "text-verified border-verified";
    animClass = animated ? "animate-stamp" : "";
    rotateStyle = "rotate(-1deg)";
  } else if (status === "BUILT" || status === "AUDITED") {
    label = status;
    colorClass = "text-ink-muted border-ink-muted";
    rotateStyle = "rotate(-0.5deg)";
  }

  return (
    <div
      style={{ transform: rotateStyle }}
      className={`inline-block select-none ${animClass} ${className}`}
      aria-label={`Status stamp: ${label}`}
    >
      <div
        className={`px-3 py-1.5 border-2 rounded-sm stamp-border uppercase tracking-widest font-mono font-bold text-center ${colorClass} bg-paper-light/60 backdrop-blur-[1px]`}
      >
        <div className="text-base sm:text-lg leading-none font-black">{label}</div>
        {(approver || date) && (
          <div className="text-[9px] sm:text-[10px] tracking-normal font-sans font-medium mt-0.5 opacity-90 border-t border-current/40 pt-0.5">
            {approver && <span>BY {approver.toUpperCase()}</span>}
            {approver && date && <span> · </span>}
            {date && <span>{new Date(date).toLocaleDateString()}</span>}
          </div>
        )}
      </div>
    </div>
  );
}
