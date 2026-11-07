"use client";

import React from "react";
import Link from "next/link";
import { ScopeResult } from "@/types";

interface ScopeInspectorProps {
  scopeResult: ScopeResult;
  plannedFiles: string[];
  touchedFiles: string[];
  offendingFiles: string[];
}

export function ScopeInspector({
  scopeResult,
  plannedFiles = [],
  touchedFiles = [],
  offendingFiles = [],
}: ScopeInspectorProps) {
  const isViolation = scopeResult === "SCOPE_VIOLATION" || offendingFiles.length > 0;

  return (
    <div className="border border-rule bg-paper-card p-5 text-sm">
      <div className="flex items-center justify-between pb-3 hairline-b">
        <div>
          <h3 className="font-serif font-bold text-lg text-ink">
            Deterministic Scope Check
          </h3>
          <p className="text-xs text-ink-muted font-sans mt-0.5">
            Clerk compares git diff touched files against authorized plan files. TouchedFiles ⊆ PlannedFiles.
          </p>
        </div>

        <div>
          {isViolation ? (
            <span className="px-2.5 py-1 text-xs font-mono font-bold uppercase bg-oxblood-faint text-oxblood border border-oxblood/40 rounded-[1px]">
              SCOPE VIOLATION
            </span>
          ) : scopeResult === "CLEAN" ? (
            <span className="px-2.5 py-1 text-xs font-mono font-bold uppercase bg-verified-faint text-verified border border-verified/40 rounded-[1px]">
              CLEAN · PASS
            </span>
          ) : (
            <span className="px-2.5 py-1 text-xs font-mono font-medium text-ink-muted border border-rule">
              PENDING
            </span>
          )}
        </div>
      </div>

      {isViolation && (
        <div className="my-4 p-3 bg-oxblood-faint/60 border border-oxblood/30 text-xs">
          <div className="font-bold text-oxblood uppercase tracking-wide">
            Unauthorized Files Detected:
          </div>
          <div className="mt-1 text-ink font-sans">
            The coding agent modified the following files which were never authorized in the approved plan:
          </div>
          <ul className="mt-2 space-y-1 font-mono text-[11px] text-oxblood font-semibold">
            {offendingFiles.map((file) => (
              <li key={file} className="flex items-center gap-1.5">
                <span className="text-oxblood">⚠</span>
                <span>{file}</span>
                <Link
                  href={`/files/${file}`}
                  className="text-xs font-sans text-ink underline ml-2 opacity-80 hover:opacity-100"
                >
                  view provenance →
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Side-by-side files table */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 text-xs font-mono">
        {/* Planned */}
        <div className="border border-rule/70 p-3 bg-paper">
          <div className="font-bold text-ink uppercase tracking-wider text-[11px] mb-2 flex items-center justify-between">
            <span>Authorized in Plan</span>
            <span className="text-ink-muted">({plannedFiles.length})</span>
          </div>
          {plannedFiles.length === 0 ? (
            <div className="text-ink-muted italic py-1">No target files specified in plan</div>
          ) : (
            <ul className="space-y-1">
              {plannedFiles.map((f) => (
                <li key={f} className="text-ink truncate py-0.5">
                  <span className="text-ink-muted mr-1.5">•</span>
                  <span>{f}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Touched */}
        <div className="border border-rule/70 p-3 bg-paper">
          <div className="font-bold text-ink uppercase tracking-wider text-[11px] mb-2 flex items-center justify-between">
            <span>Touched in Git Diff</span>
            <span className="text-ink-muted">({touchedFiles.length})</span>
          </div>
          {touchedFiles.length === 0 ? (
            <div className="text-ink-muted italic py-1">No git diff captured yet</div>
          ) : (
            <ul className="space-y-1">
              {touchedFiles.map((f) => {
                const isOffending = offendingFiles.includes(f);
                return (
                  <li
                    key={f}
                    className={`truncate py-0.5 flex items-center justify-between ${
                      isOffending ? "text-oxblood font-bold" : "text-ink"
                    }`}
                  >
                    <span className="truncate">
                      <span className="mr-1.5">{isOffending ? "✕" : "✓"}</span>
                      {f}
                    </span>
                    <Link
                      href={`/files/${f}`}
                      className="text-[10px] font-sans text-ink-muted underline hover:text-ink shrink-0 ml-1"
                    >
                      history
                    </Link>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
