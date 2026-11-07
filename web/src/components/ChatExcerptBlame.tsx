"use client";

import React, { useState } from "react";
import Link from "next/link";

interface BlameLine {
  lineNum: number;
  type: "unchanged" | "added" | "removed";
  code: string;
  warrantId?: string;
  author?: string;
  chatExcerpt?: string;
  timestamp?: string;
  scopeStatus?: "CLEAN" | "SCOPE_VIOLATION";
}

const SAMPLE_BLAME_LINES: BlameLine[] = [
  {
    lineNum: 14,
    type: "unchanged",
    code: "def calculate_tax(items, tax_rate=0.20):",
  },
  {
    lineNum: 15,
    type: "unchanged",
    code: "    total_tax = 0.0",
  },
  {
    lineNum: 16,
    type: "unchanged",
    code: "    for item in items:",
  },
  {
    lineNum: 17,
    type: "added",
    code: '        if item.get("tax_exempt", False):',
    warrantId: "W-014",
    author: "priya",
    chatExcerpt: "Priya in #warrant-room: 'approve W-014 a3f9c2'",
    timestamp: "Nov 7, 2026, 09:05 UTC",
    scopeStatus: "CLEAN",
  },
  {
    lineNum: 18,
    type: "added",
    code: "            continue",
    warrantId: "W-014",
    author: "priya",
    chatExcerpt: "Priya in #warrant-room: 'approve W-014 a3f9c2'",
    timestamp: "Nov 7, 2026, 09:05 UTC",
    scopeStatus: "CLEAN",
  },
  {
    lineNum: 19,
    type: "unchanged",
    code: '        total_tax += item["price"] * item["quantity"] * tax_rate',
  },
  {
    lineNum: 20,
    type: "unchanged",
    code: "    return round(total_tax, 2)",
  },
];

export function ChatExcerptBlame() {
  const [selectedLine, setSelectedLine] = useState<number>(17);
  const activeExcerpt = SAMPLE_BLAME_LINES.find((l) => l.lineNum === selectedLine) || SAMPLE_BLAME_LINES[3];

  return (
    <div className="border border-rule bg-paper-card p-5 sm:p-6 text-sm">
      <div className="pb-4 hairline-b flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <span className="text-[11px] font-mono uppercase tracking-widest text-ink-muted">
            Warrant Provenance Inspector
          </span>
          <h3 className="font-serif font-bold text-xl text-ink">
            Git Blame Bound to Human Chat Authorization
          </h3>
          <p className="text-xs text-ink-muted mt-0.5">
            Hover or click a modified line to inspect the Switch room evidence and human approval that authorized it.
          </p>
        </div>

        <div className="font-mono text-xs text-ink-muted self-start sm:self-auto">
          File: <span className="text-ink font-semibold">src/invoice/calculator.py</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-4">
        {/* Code View */}
        <div className="lg:col-span-7 font-mono text-xs border border-rule/70 bg-paper overflow-x-auto">
          <div className="px-3 py-1.5 bg-paper-dark/30 text-[11px] text-ink-muted hairline-b">
            diff --git a/src/invoice/calculator.py b/src/invoice/calculator.py
          </div>
          <div className="py-2">
            {SAMPLE_BLAME_LINES.map((line) => {
              const isSelected = selectedLine === line.lineNum;
              const isAdded = line.type === "added";

              return (
                <div
                  key={line.lineNum}
                  onClick={() => line.warrantId && setSelectedLine(line.lineNum)}
                  className={`flex items-center px-3 py-0.5 cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-paper-dark font-semibold ring-1 ring-inset ring-rule-dark"
                      : isAdded
                      ? "bg-verified-faint/50 hover:bg-verified-faint"
                      : "hover:bg-paper-dark/20 text-ink-muted"
                  }`}
                >
                  <span className="w-8 text-right text-ink-muted/60 select-none mr-3 text-[11px]">
                    {line.lineNum}
                  </span>
                  <span className="w-4 select-none text-[11px]">
                    {line.type === "added" ? "+" : " "}
                  </span>
                  <span className={`truncate ${isAdded ? "text-ink font-medium" : "text-ink-muted"}`}>
                    {line.code}
                  </span>
                  {line.warrantId && (
                    <span className="ml-auto pl-2 text-[10px] uppercase font-mono text-ink-muted select-none">
                      [{line.warrantId}]
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Originating Chat Evidence Card */}
        <div className="lg:col-span-5 flex flex-col justify-between border border-rule/80 p-4 bg-paper-light">
          <div>
            <div className="flex items-center justify-between pb-2 hairline-b">
              <span className="text-[10px] font-mono uppercase tracking-wider text-ink-muted">
                Originating Switch Evidence
              </span>
              <span className="px-1.5 py-0.5 text-[9px] font-mono font-bold uppercase bg-verified-faint text-verified border border-verified/30 rounded-[1px]">
                {activeExcerpt.scopeStatus}
              </span>
            </div>

            <div className="mt-3 space-y-3 text-xs">
              <div>
                <span className="text-[10px] font-mono text-ink-muted uppercase">Authorized By</span>
                <div className="font-semibold text-ink text-sm">
                  @{activeExcerpt.author}{" "}
                  <span className="text-xs font-normal text-ink-muted">
                    ({activeExcerpt.timestamp})
                  </span>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-mono text-ink-muted uppercase">
                  Verifiable Chat Excerpt
                </span>
                <blockquote className="mt-1 p-2.5 bg-paper border-l-2 border-oxblood font-mono text-xs text-ink leading-relaxed">
                  {activeExcerpt.chatExcerpt}
                </blockquote>
              </div>

              <div>
                <span className="text-[10px] font-mono text-ink-muted uppercase">
                  Warrant Record Reference
                </span>
                <div className="mt-1 font-mono text-xs">
                  <Link
                    href={`/w/${activeExcerpt.warrantId}`}
                    className="text-oxblood font-bold underline hover:opacity-80"
                  >
                    {activeExcerpt.warrantId} (Inspect Hash Proof) →
                  </Link>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 hairline-t mt-4 text-[11px] font-mono text-ink-muted">
            Without Switch shared history, this change would be an unattributed git commit.
          </div>
        </div>
      </div>
    </div>
  );
}
