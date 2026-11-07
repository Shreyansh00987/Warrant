"use client";

import React from "react";
import Link from "next/link";
import { Warrant } from "@/types";
import { Stamp } from "./Stamp";

interface WarrantCardProps {
  warrant: Warrant;
  showLinks?: boolean;
  className?: string;
}

export function WarrantCard({
  warrant,
  showLinks = true,
  className = "",
}: WarrantCardProps) {
  const isOutOfScope = warrant.status === "OUT_OF_SCOPE" || warrant.scope_result === "SCOPE_VIOLATION";
  const isApproved = warrant.status === "APPROVED_MERGE" || warrant.status === "APPROVED_PLAN";

  return (
    <article
      className={`relative paper-texture text-ink double-border p-6 sm:p-8 shadow-warrant rounded-[1px] ${className}`}
      aria-label={`Warrant ${warrant.id}`}
    >
      {/* Top Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-5 hairline-b">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono uppercase tracking-widest text-ink-muted">
              Warrant of Authorization
            </span>
            {warrant.source === "seeded" && (
              <span className="text-[9px] font-mono uppercase tracking-widest px-1.5 py-0.5 border border-rule text-ink-muted bg-paper-dark/40">
                Seeded Demo Data
              </span>
            )}
          </div>
          <h2 className="text-2xl sm:text-3xl font-serif font-bold tracking-tight mt-1 text-ink">
            {warrant.id}
          </h2>
          <div className="text-xs font-mono text-ink-muted mt-1">
            Switch Room: <span className="text-ink">{warrant.room_id}</span>
          </div>
        </div>

        {/* The Rubber Stamp */}
        <div className="self-end sm:self-start">
          <Stamp
            status={warrant.status}
            approver={warrant.approved_by}
            date={warrant.approved_at}
          />
        </div>
      </div>

      {/* Main Warrant Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 py-6 hairline-b text-sm">
        {/* Left Column: Intent & Plan */}
        <div className="space-y-4">
          <div>
            <div className="text-[11px] font-mono uppercase tracking-wider text-ink-muted">
              Authorized Intent
            </div>
            <p className="mt-1 text-ink font-sans leading-relaxed">
              Requested by <span className="font-semibold">{warrant.requester}</span> in Switch chat.
            </p>
          </div>

          <div>
            <div className="text-[11px] font-mono uppercase tracking-wider text-ink-muted">
              Bound Plan SHA-256 Hash
            </div>
            <div className="mt-1 font-mono text-xs text-ink break-all bg-paper-dark/30 p-2 border border-rule/60 rounded-[1px]">
              {warrant.plan_hash ? (
                <>
                  <span className="font-bold text-oxblood">{warrant.plan_hash.slice(0, 8)}</span>
                  <span className="opacity-70">{warrant.plan_hash.slice(8)}</span>
                </>
              ) : (
                <span className="text-ink-muted italic">No plan hash recorded</span>
              )}
            </div>
          </div>

          <div>
            <div className="text-[11px] font-mono uppercase tracking-wider text-ink-muted">
              Human Approver
            </div>
            <div className="mt-1 font-sans">
              {warrant.approved_by ? (
                <span className="font-medium text-ink">
                  {warrant.approved_by}{" "}
                  <span className="text-xs text-ink-muted">
                    ({warrant.approved_at ? new Date(warrant.approved_at).toLocaleString() : "time unrecorded"})
                  </span>
                </span>
              ) : (
                <span className="text-ink-muted italic">Awaiting human approval</span>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Execution & Scope Result */}
        <div className="space-y-4">
          <div>
            <div className="text-[11px] font-mono uppercase tracking-wider text-ink-muted">
              Execution Target & Commit
            </div>
            <div className="mt-1 font-mono text-xs text-ink space-y-1">
              <div>
                Branch: <span className="font-semibold">{warrant.branch || "unassigned"}</span>
              </div>
              <div className="break-all">
                Commit:{" "}
                {warrant.commit_sha ? (
                  <span className="bg-paper-dark/40 px-1 py-0.5 border border-rule/50">
                    {warrant.commit_sha.slice(0, 10)}
                  </span>
                ) : (
                  <span className="text-ink-muted italic">pending build</span>
                )}
              </div>
            </div>
          </div>

          <div>
            <div className="text-[11px] font-mono uppercase tracking-wider text-ink-muted">
              Deterministic Scope Check
            </div>
            <div className="mt-1">
              {isOutOfScope ? (
                <div className="bg-oxblood-faint border border-oxblood/40 p-2.5 rounded-[1px] text-xs">
                  <span className="font-bold text-oxblood uppercase tracking-wide">
                    Scope Violation Detected
                  </span>
                  <div className="mt-1 text-ink">
                    Agent modified unauthorized file(s):
                    <ul className="list-disc list-inside mt-1 font-mono text-[11px] text-oxblood font-semibold">
                      {warrant.offending_files?.map((f) => (
                        <li key={f}>{f}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : warrant.scope_result === "CLEAN" ? (
                <div className="bg-verified-faint border border-verified/40 p-2 rounded-[1px] text-xs font-mono text-verified font-medium flex items-center gap-1.5">
                  <span>✓</span> Scope Clean: Touched files strictly match approved plan.
                </div>
              ) : (
                <div className="text-xs text-ink-muted italic">Scope check pending diff emission</div>
              )}
            </div>
          </div>

          <div>
            <div className="text-[11px] font-mono uppercase tracking-wider text-ink-muted">
              Independent Auditor Verdict
            </div>
            <div className="mt-1 text-xs">
              {warrant.auditor_verdict === "PASS" ? (
                <span className="font-bold text-verified uppercase">PASS (Codex)</span>
              ) : warrant.auditor_verdict === "BLOCK" ? (
                <span className="font-bold text-oxblood uppercase">BLOCK (Codex)</span>
              ) : (
                <span className="text-ink-muted italic">Pending auditor review</span>
              )}
              {warrant.auditor_notes && (
                <p className="text-ink-muted text-xs mt-0.5 italic">{warrant.auditor_notes}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Hash-Chain Strip */}
      <div className="pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-[11px] font-mono text-ink-muted">
        <div className="space-y-0.5 truncate max-w-xl">
          <div className="truncate">
            Prev Hash: <span className="text-ink">{warrant.prev_hash.slice(0, 16)}...</span>
          </div>
          <div className="truncate font-semibold text-ink">
            Record Hash: <span>{warrant.record_hash ? warrant.record_hash.slice(0, 24) + "..." : "uncomputed"}</span>
          </div>
        </div>

        {showLinks && (
          <div className="flex items-center gap-3">
            <Link
              href={`/w/${warrant.id}`}
              className="text-ink underline hover:text-oxblood font-sans text-xs font-semibold"
            >
              Inspect Proof & Events →
            </Link>
          </div>
        )}
      </div>
    </article>
  );
}
