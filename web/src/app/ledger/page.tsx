"use client";

import React, { useEffect, useState, useCallback, useTransition, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Warrant, StatsResponse } from "@/types";
import { fetchWarrants, fetchStats, fetchVerification, seedDatabase } from "@/lib/api";
import { Stamp } from "@/components/Stamp";

function LedgerContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const verifyParam = searchParams.get("verify");

  const [warrants, setWarrants] = useState<Warrant[]>([]);
  const [stats, setStats] = useState<StatsResponse>({
    total: 0,
    approved: 0,
    out_of_scope: 0,
    blocked: 0,
    pending: 0,
    live_count: 0,
    seeded_count: 0,
  });
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [filterSource, setFilterSource] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [verifyResult, setVerifyResult] = useState<any>(null);
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [isPending, startTransition] = useTransition();

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const src = filterSource === "all" ? undefined : filterSource;
      const stat = filterStatus === "all" ? undefined : filterStatus;
      const [wList, sData] = await Promise.all([
        fetchWarrants(src, stat),
        fetchStats(),
      ]);
      setWarrants(wList);
      setStats(sData);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [filterSource, filterStatus]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle ?verify=<sha> param
  useEffect(() => {
    if (verifyParam) {
      setIsVerifying(true);
      fetchVerification(verifyParam).then((res) => {
        setVerifyResult(res);
        setIsVerifying(false);
      });
    } else {
      setVerifyResult(null);
    }
  }, [verifyParam]);

  // Keyboard Navigation: j/k to move, Enter to open, Esc to clear
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't intercept if user is typing in an input
      if (
        document.activeElement?.tagName === "INPUT" ||
        document.activeElement?.tagName === "TEXTAREA"
      ) {
        return;
      }

      if (e.key === "j" || e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev < warrants.length - 1 ? prev + 1 : prev));
      } else if (e.key === "k" || e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : 0));
      } else if (e.key === "Enter") {
        if (warrants[selectedIndex]) {
          router.push(`/w/${warrants[selectedIndex].id}`);
        }
      } else if (e.key === "Escape") {
        setVerifyResult(null);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [warrants, selectedIndex, router]);

  const handleSeed = async () => {
    setIsLoading(true);
    await seedDatabase();
    await loadData();
    setIsLoading(false);
  };

  return (
    <div className="space-y-8">
      {/* Page Title & Counters */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 hairline-b">
        <div>
          <span className="text-[11px] font-mono uppercase tracking-widest text-ink-muted">
            The Hash-Linked Ledger
          </span>
          <h1 className="text-3xl font-serif font-black tracking-tight text-ink mt-1">
            Warrant Authorization Ledger
          </h1>
          <p className="text-xs text-ink-muted mt-1 font-sans">
            Use <kbd className="px-1 py-0.5 border border-rule bg-paper-light font-mono text-[10px]">j</kbd> /{" "}
            <kbd className="px-1 py-0.5 border border-rule bg-paper-light font-mono text-[10px]">k</kbd> to
            navigate, <kbd className="px-1 py-0.5 border border-rule bg-paper-light font-mono text-[10px]">Enter</kbd> to
            view, <kbd className="px-1 py-0.5 border border-rule bg-paper-light font-mono text-[10px]">Esc</kbd> to dismiss.
          </p>
        </div>

        {/* Dense Counter Strip */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="text-right">
            <span className="text-[10px] text-ink-muted uppercase block">Approved</span>
            <span className="text-base font-bold text-ink tabular-nums">{stats.approved}</span>
          </div>
          <div className="h-6 w-[1px] bg-rule" />
          <div className="text-right">
            <span className="text-[10px] text-ink-muted uppercase block">Out of Scope</span>
            <span className="text-base font-bold text-oxblood tabular-nums">{stats.out_of_scope}</span>
          </div>
          <div className="h-6 w-[1px] bg-rule" />
          <div className="text-right">
            <span className="text-[10px] text-ink-muted uppercase block">Blocked</span>
            <span className="text-base font-bold text-ink-muted tabular-nums">{stats.blocked}</span>
          </div>
          <div className="h-6 w-[1px] bg-rule" />
          <div className="text-right">
            <span className="text-[10px] text-ink-muted uppercase block">Total</span>
            <span className="text-base font-bold text-ink tabular-nums">{stats.total}</span>
          </div>
        </div>
      </div>

      {/* Verification Drawer if triggered */}
      {verifyResult && (
        <div
          className={`p-5 border text-xs font-mono transition-all ${
            verifyResult.verified
              ? "bg-verified-faint border-verified/50 text-ink"
              : "bg-oxblood-faint border-oxblood/50 text-ink"
          }`}
        >
          <div className="flex items-center justify-between pb-2 hairline-b">
            <div className="flex items-center gap-2">
              <span
                className={`font-black text-sm uppercase ${
                  verifyResult.verified ? "text-verified" : "text-oxblood"
                }`}
              >
                [{verifyResult.status}]
              </span>
              <span className="font-semibold text-ink">Commit: {verifyResult.commit_sha}</span>
            </div>
            <button
              onClick={() => setVerifyResult(null)}
              className="text-xs font-sans text-ink-muted hover:text-ink"
            >
              Close [Esc] ✕
            </button>
          </div>
          <p className="mt-2 text-xs font-sans">{verifyResult.reason}</p>
          {verifyResult.warrant && (
            <div className="mt-3 pt-2 hairline-t flex items-center gap-4 text-[11px]">
              <span>Warrant: <strong className="text-ink">{verifyResult.warrant.id}</strong></span>
              <span>Approver: <strong className="text-ink">{verifyResult.warrant.approved_by}</strong></span>
              <Link
                href={`/w/${verifyResult.warrant.id}`}
                className="underline text-oxblood font-semibold ml-auto font-sans"
              >
                View Full Card & Proof →
              </Link>
            </div>
          )}
        </div>
      )}

      {/* Filter Tabs Strip */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs font-mono pb-2 hairline-b">
        <div className="flex items-center gap-2">
          <span className="text-ink-muted text-[11px] uppercase mr-1">Filter:</span>
          {["all", "APPROVED_MERGE", "OUT_OF_SCOPE", "BLOCKED"].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-2.5 py-1 rounded-[1px] transition-colors ${
                filterStatus === st
                  ? "bg-ink text-paper font-bold"
                  : "bg-paper-light border border-rule hover:border-ink text-ink"
              }`}
            >
              {st === "all" ? "All Statuses" : st.replace("_", " ")}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-ink-muted text-[11px] uppercase mr-1">Source:</span>
          {["all", "live", "seeded"].map((src) => (
            <button
              key={src}
              onClick={() => setFilterSource(src)}
              className={`px-2.5 py-1 rounded-[1px] uppercase text-[10px] transition-colors ${
                filterSource === src
                  ? "bg-ink text-paper font-bold"
                  : "bg-paper-light border border-rule hover:border-ink text-ink"
              }`}
            >
              {src}
            </button>
          ))}
        </div>
      </div>

      {/* Dense Ledger Table */}
      {isLoading ? (
        <div className="py-16 text-center text-xs font-mono text-ink-muted">
          Loading warrant records from Clerk...
        </div>
      ) : warrants.length === 0 ? (
        <div className="py-16 text-center border border-rule p-8 bg-paper-card text-sm">
          <h3 className="font-serif font-bold text-lg text-ink">No Warrants on Record</h3>
          <p className="text-xs text-ink-muted mt-1 max-w-md mx-auto font-sans">
            No matching warrants were found in the database. You can seed realistic demo warrants (W-014 pass & W-015 drift)
            or run events through Switch.
          </p>
          <button
            onClick={handleSeed}
            className="mt-4 px-4 py-2 bg-ink text-paper text-xs font-mono uppercase tracking-wider font-semibold rounded-[1px] hover:bg-oxblood transition-colors"
          >
            Seed Demo Data (W-014 & W-015)
          </button>
        </div>
      ) : (
        <div className="border border-rule bg-paper overflow-x-auto shadow-sm">
          <table className="w-full text-left text-xs font-mono border-collapse" role="table">
            <thead>
              <tr className="hairline-b bg-paper-dark/30 text-[11px] text-ink-muted uppercase">
                <th className="py-2.5 px-4 w-12 text-center">#</th>
                <th className="py-2.5 px-4 w-28">Warrant ID</th>
                <th className="py-2.5 px-4">Authorized Intent / Task</th>
                <th className="py-2.5 px-4 w-28">Approver</th>
                <th className="py-2.5 px-4 w-32">Status</th>
                <th className="py-2.5 px-4 w-28">Commit</th>
                <th className="py-2.5 px-4 w-24">Source</th>
                <th className="py-2.5 px-4 w-28 text-right">Time</th>
              </tr>
            </thead>
            <tbody>
              {warrants.map((w, idx) => {
                const isSelected = selectedIndex === idx;
                const isViolation = w.status === "OUT_OF_SCOPE" || w.scope_result === "SCOPE_VIOLATION";
                const isApproved = w.status === "APPROVED_MERGE";

                return (
                  <tr
                    key={w.id}
                    onClick={() => {
                      setSelectedIndex(idx);
                      router.push(`/w/${w.id}`);
                    }}
                    className={`hairline-b cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-paper-dark/80 font-medium"
                        : "hover:bg-paper-dark/30"
                    }`}
                  >
                    <td className="py-3 px-4 text-center text-ink-muted/50 select-none">
                      {isSelected ? "▶" : idx + 1}
                    </td>
                    <td className="py-3 px-4 font-bold text-ink underline hover:text-oxblood">
                      <Link href={`/w/${w.id}`}>{w.id}</Link>
                    </td>
                    <td className="py-3 px-4 font-sans text-xs text-ink max-w-md truncate">
                      {w.plan_md ? (
                        w.plan_md.replace(/###|`|-/g, "").slice(0, 75).trim() + "..."
                      ) : (
                        <span className="text-ink-muted italic">Requested by {w.requester}</span>
                      )}
                    </td>
                    <td className="py-3 px-4 font-sans text-xs text-ink font-medium">
                      {w.approved_by ? `@${w.approved_by}` : <span className="text-ink-muted">—</span>}
                    </td>
                    <td className="py-3 px-4">
                      {isViolation ? (
                        <span className="px-2 py-0.5 text-[10px] font-bold text-oxblood bg-oxblood-faint border border-oxblood/30 rounded-[1px]">
                          OUT OF SCOPE
                        </span>
                      ) : isApproved ? (
                        <span className="px-2 py-0.5 text-[10px] font-bold text-verified bg-verified-faint border border-verified/30 rounded-[1px]">
                          APPROVED
                        </span>
                      ) : (
                        <span className="px-1.5 py-0.5 text-[10px] text-ink-muted border border-rule">
                          {w.status}
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-ink-muted text-[11px]">
                      {w.commit_sha ? (
                        <span>{w.commit_sha.slice(0, 7)}</span>
                      ) : (
                        <span>—</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-[10px] uppercase text-ink-muted tracking-wider">
                        {w.source}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right text-ink-muted text-[11px] tabular-nums">
                      {new Date(w.created_at).toLocaleDateString([], {
                        month: "short",
                        day: "numeric",
                      })}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function LedgerPage() {
  return (
    <Suspense fallback={<div className="py-20 text-center font-mono text-xs text-ink-muted">Loading ledger...</div>}>
      <LedgerContent />
    </Suspense>
  );
}
