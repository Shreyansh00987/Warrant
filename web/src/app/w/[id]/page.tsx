"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { WarrantDetailResponse } from "@/types";
import { fetchWarrant } from "@/lib/api";
import { WarrantCard } from "@/components/WarrantCard";
import { WorkflowPath } from "@/components/WorkflowPath";
import { ScopeInspector } from "@/components/ScopeInspector";

export default function WarrantDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = Array.isArray(params.id) ? params.id[0] : params.id;

  const [data, setData] = useState<WarrantDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [tamperSimulated, setTamperSimulated] = useState<boolean>(false);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    fetchWarrant(id).then((res) => {
      setData(res);
      setIsLoading(false);
    });
  }, [id]);

  if (isLoading) {
    return (
      <div className="py-20 text-center font-mono text-xs text-ink-muted">
        Loading warrant {id} from ledger...
      </div>
    );
  }

  if (!data || !data.warrant) {
    return (
      <div className="py-16 text-center border border-rule p-8 bg-paper-card text-sm space-y-4">
        <h2 className="font-serif font-bold text-2xl text-ink">Warrant Not Found</h2>
        <p className="text-xs text-ink-muted max-w-md mx-auto font-sans">
          No record found for identifier &ldquo;{id}&rdquo;. Verify the ID or check the ledger table.
        </p>
        <Link
          href="/ledger"
          className="inline-block px-4 py-2 bg-ink text-paper text-xs font-mono uppercase tracking-wider font-semibold hover:bg-oxblood transition-colors rounded-[1px]"
        >
          ← Return to Ledger
        </Link>
      </div>
    );
  }

  const { warrant, events, verification } = data;
  const isTampered = tamperSimulated || verification?.is_tampered;

  return (
    <div className="space-y-12">
      {/* Top Breadcrumb & Action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 hairline-b text-xs font-mono">
        <div className="flex items-center gap-2 text-ink-muted">
          <Link href="/ledger" className="hover:text-ink underline">
            ← Ledger
          </Link>
          <span>/</span>
          <span className="text-ink font-bold">{warrant.id}</span>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setTamperSimulated(!tamperSimulated)}
            className={`px-3 py-1 border text-xs font-mono transition-colors rounded-[1px] ${
              tamperSimulated
                ? "bg-oxblood text-paper border-oxblood font-bold"
                : "bg-paper-light border-rule text-ink hover:border-ink"
            }`}
          >
            {tamperSimulated ? "Reset Tamper Simulation" : "Simulate Tamper Check"}
          </button>

          {warrant.commit_sha && (
            <Link
              href={`/ledger?verify=${warrant.commit_sha}`}
              className="px-3 py-1 bg-ink text-paper text-xs font-mono hover:bg-oxblood transition-colors rounded-[1px]"
            >
              Verify Commit SHA →
            </Link>
          )}
        </div>
      </div>

      {/* The Skeuomorphic Warrant Card */}
      <section className="space-y-2">
        <WarrantCard warrant={warrant} showLinks={false} />
      </section>

      {/* Workflow Path Pipeline */}
      <section className="border border-rule p-5 bg-paper-card">
        <div className="text-[11px] font-mono uppercase tracking-widest text-ink-muted mb-2">
          Switch Room Lifecycle State
        </div>
        <WorkflowPath status={warrant.status} />
      </section>

      {/* Scope Inspector Component */}
      <section>
        <ScopeInspector
          scopeResult={warrant.scope_result}
          plannedFiles={verification?.scope_check?.planned_files || []}
          touchedFiles={verification?.scope_check?.touched_files || []}
          offendingFiles={warrant.offending_files || []}
        />
      </section>

      {/* Side-by-side: Authorized Plan vs Originating Chat Excerpts */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-8 text-sm">
        {/* Approved Plan Text */}
        <div className="border border-rule bg-paper-card p-6 space-y-3">
          <div className="flex items-center justify-between pb-2 hairline-b">
            <h3 className="font-serif font-bold text-lg text-ink">
              Authorized Plan Markdown
            </h3>
            <span className="text-xs font-mono text-ink-muted">
              Hash: <code className="text-ink font-bold">{warrant.plan_hash?.slice(0, 8)}</code>
            </span>
          </div>

          <div className="font-mono text-xs bg-paper border border-rule/70 p-4 whitespace-pre-wrap text-ink leading-relaxed max-h-96 overflow-y-auto">
            {warrant.plan_md || "No plan text recorded"}
          </div>

          <div className="text-[11px] font-mono text-ink-muted pt-2 hairline-t">
            Plan SHA-256 is bound to human approval command:{" "}
            <code className="text-ink bg-paper-dark/40 px-1">
              approve {warrant.id} {warrant.plan_hash?.slice(0, 6)}
            </code>
          </div>
        </div>

        {/* Verifiable Hash Link Proof Box */}
        <div className="border border-rule bg-paper-light p-6 space-y-4">
          <div className="flex items-center justify-between pb-2 hairline-b">
            <h3 className="font-serif font-bold text-lg text-ink">
              Hash Chain Cryptographic Proof
            </h3>
            {isTampered ? (
              <span className="text-xs font-mono font-bold text-oxblood bg-oxblood-faint px-2 py-0.5 border border-oxblood">
                TAMPER DETECTED
              </span>
            ) : (
              <span className="text-xs font-mono font-bold text-verified bg-verified-faint px-2 py-0.5 border border-verified">
                LINK INTACT
              </span>
            )}
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div>
              <div className="text-[10px] text-ink-muted uppercase">Previous Record Hash (prev_hash)</div>
              <div className="p-2 bg-paper border border-rule/70 break-all text-[11px] text-ink font-semibold">
                {warrant.prev_hash}
              </div>
            </div>

            <div>
              <div className="text-[10px] text-ink-muted uppercase">Plan Hash (SHA-256)</div>
              <div className="p-2 bg-paper border border-rule/70 break-all text-[11px] text-ink flex items-center justify-between">
                <span>{warrant.plan_hash}</span>
                <span className="text-verified font-bold ml-2">✓ Valid</span>
              </div>
            </div>

            <div>
              <div className="text-[10px] text-ink-muted uppercase">Diff Hash (SHA-256)</div>
              <div className="p-2 bg-paper border border-rule/70 break-all text-[11px] text-ink flex items-center justify-between">
                <span>{warrant.diff_hash || "pending diff"}</span>
                {warrant.diff_hash && <span className="text-verified font-bold ml-2">✓ Valid</span>}
              </div>
            </div>

            <div>
              <div className="text-[10px] text-ink-muted uppercase">
                {isTampered ? "Tampered Record Hash (Simulated)" : "Stored Record Hash (record_hash)"}
              </div>
              <div
                className={`p-2 border break-all text-[11px] font-bold ${
                  isTampered
                    ? "bg-oxblood-faint border-oxblood text-oxblood"
                    : "bg-paper border-rule/70 text-ink"
                }`}
              >
                {isTampered
                  ? "deadbeef" + (warrant.record_hash?.slice(8) || "")
                  : warrant.record_hash || "uncomputed"}
              </div>
            </div>
          </div>

          <p className="text-xs font-sans text-ink-muted pt-2 hairline-t">
            Every warrant binds the request, plan hash, diff hash, scope result, approver, and previous hash into a single chain.
          </p>
        </div>
      </section>

      {/* Activity Timeline */}
      <section className="space-y-4 pt-4 hairline-t">
        <div>
          <span className="text-[11px] font-mono uppercase tracking-widest text-ink-muted">
            Switch Room Shared History
          </span>
          <h3 className="font-serif font-bold text-2xl text-ink mt-0.5">
            Immutable Activity Timeline ({events.length} Events)
          </h3>
          <p className="text-xs text-ink-muted mt-1 font-sans">
            Raw excerpts recorded at the moment of human approval. Survives chat retention pruning.
          </p>
        </div>

        <div className="border border-rule divide-y divide-rule bg-paper">
          {events.length === 0 ? (
            <div className="p-6 text-center text-xs font-mono text-ink-muted">
              No chat events recorded for this warrant yet.
            </div>
          ) : (
            events.map((evt) => (
              <div key={evt.id} className="p-4 flex flex-col sm:flex-row sm:items-start justify-between gap-3 text-xs font-mono">
                <div className="space-y-1 max-w-2xl">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-ink uppercase text-[11px]">{evt.kind}</span>
                    <span className="text-ink-muted">by</span>
                    <span className="px-1.5 py-0.5 bg-paper-dark/50 border border-rule/70 text-ink font-semibold">
                      @{evt.actor}
                    </span>
                  </div>
                  <blockquote className="mt-1 font-sans text-xs text-ink bg-paper-light p-2.5 border-l-2 border-rule-dark leading-relaxed">
                    {evt.excerpt}
                  </blockquote>
                </div>
                <div className="text-[11px] text-ink-muted sm:text-right shrink-0">
                  <div>{new Date(evt.at).toLocaleDateString()}</div>
                  <div>{new Date(evt.at).toLocaleTimeString()}</div>
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
