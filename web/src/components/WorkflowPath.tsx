"use client";

import React from "react";
import { WarrantStatus } from "@/types";

interface WorkflowPathProps {
  status: WarrantStatus;
}

const STEPS = [
  { key: "request", label: "Request", matchStatuses: ["REQUESTED", "PLANNED", "APPROVED_PLAN", "BUILT", "AUDITED", "APPROVED_MERGE"] },
  { key: "plan", label: "Plan", matchStatuses: ["PLANNED", "APPROVED_PLAN", "BUILT", "AUDITED", "APPROVED_MERGE"] },
  { key: "approve", label: "Approve Plan", matchStatuses: ["APPROVED_PLAN", "BUILT", "AUDITED", "APPROVED_MERGE"] },
  { key: "build", label: "Build & Scope", matchStatuses: ["BUILT", "AUDITED", "APPROVED_MERGE"] },
  { key: "audit", label: "Audit Review", matchStatuses: ["AUDITED", "APPROVED_MERGE"] },
  { key: "merge", label: "Merge Gate", matchStatuses: ["APPROVED_MERGE"] },
];

export function WorkflowPath({ status }: WorkflowPathProps) {
  const isOutOfScope = status === "OUT_OF_SCOPE";
  const isBlocked = status === "BLOCKED";

  // Determine current active step index
  let activeIndex = 0;
  if (status === "REQUESTED") activeIndex = 0;
  else if (status === "PLANNED") activeIndex = 1;
  else if (status === "APPROVED_PLAN") activeIndex = 2;
  else if (status === "BUILT" || isOutOfScope) activeIndex = 3;
  else if (status === "AUDITED" || isBlocked) activeIndex = 4;
  else if (status === "APPROVED_MERGE") activeIndex = 5;

  return (
    <div className="w-full py-4 overflow-x-auto" aria-label="Workflow progress">
      <div className="flex items-center min-w-[580px] justify-between text-xs font-mono">
        {STEPS.map((step, idx) => {
          const isCompleted = idx < activeIndex;
          const isCurrent = idx === activeIndex;
          const isFailedStep = (isOutOfScope && idx === 3) || (isBlocked && idx === 4);

          let circleClass = "border-rule text-ink-muted bg-paper-light";
          let textClass = "text-ink-muted";

          if (isFailedStep) {
            circleClass = "border-oxblood bg-oxblood text-paper font-bold";
            textClass = "text-oxblood font-bold";
          } else if (isCurrent) {
            circleClass = "border-ink bg-paper-dark text-ink font-bold animate-pulse-subtle ring-2 ring-ink/20";
            textClass = "text-ink font-bold";
          } else if (isCompleted) {
            circleClass = "border-rule-dark bg-paper-dark text-ink";
            textClass = "text-ink font-medium";
          }

          return (
            <React.Fragment key={step.key}>
              <div className="flex flex-col items-center gap-1.5 flex-1 text-center">
                <div
                  className={`w-7 h-7 rounded-full border flex items-center justify-center text-[11px] transition-all ${circleClass}`}
                >
                  {isFailedStep ? "✕" : isCompleted ? "✓" : idx + 1}
                </div>
                <span className={`text-[11px] leading-tight ${textClass}`}>
                  {step.label}
                  {isFailedStep && (
                    <span className="block text-[9px] uppercase tracking-wider text-oxblood">
                      {isOutOfScope ? "Failed Scope" : "Blocked"}
                    </span>
                  )}
                </span>
              </div>

              {idx < STEPS.length - 1 && (
                <div
                  className={`h-[1px] flex-1 -mt-4 transition-colors ${
                    idx < activeIndex ? "bg-ink" : "bg-rule"
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
