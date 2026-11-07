"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { FileProvenanceRecord } from "@/types";
import { fetchFileProvenance } from "@/lib/api";

const PRESET_FILES = [
  "src/invoice/calculator.py",
  "src/invoice/formatter.py",
  "src/payments/stripe_gateway.py",
  "tests/test_calculator.py",
];

export default function FileProvenancePage() {
  const params = useParams();
  const rawPath = params.path;
  const filePath = Array.isArray(rawPath) ? rawPath.join("/") : rawPath || "";

  const [records, setRecords] = useState<FileProvenanceRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!filePath) return;
    setIsLoading(true);
    fetchFileProvenance(filePath).then((res) => {
      setRecords(res);
      setIsLoading(false);
    });
  }, [filePath]);

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="pb-4 hairline-b">
        <span className="text-[11px] font-mono uppercase tracking-widest text-ink-muted">
          File Authorization Audit Trail
        </span>
        <h1 className="text-3xl font-serif font-black tracking-tight text-ink mt-1 break-all">
          {filePath}
        </h1>
        <p className="text-xs text-ink-muted mt-1 font-sans">
          Every human authorization that permitted modifications to this file.
        </p>
      </div>

      {/* Preset file quick selector */}
      <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
        <span className="text-ink-muted text-[11px] uppercase mr-1">Demo Files:</span>
        {PRESET_FILES.map((f) => (
          <Link
            key={f}
            href={`/files/${f}`}
            className={`px-2.5 py-1 rounded-[1px] transition-colors border ${
              f === filePath
                ? "bg-ink text-paper font-bold border-ink"
                : "bg-paper-light border-rule text-ink hover:border-ink"
            }`}
          >
            {f}
          </Link>
        ))}
      </div>

      {/* Provenance Results */}
      {isLoading ? (
        <div className="py-16 text-center font-mono text-xs text-ink-muted">
          Fetching provenance records from Clerk...
        </div>
      ) : records.length === 0 ? (
        <div className="border border-rule p-8 bg-paper-card text-center text-sm space-y-3">
          <h3 className="font-serif font-bold text-lg text-ink">
            No Warrant Authorizations Found
          </h3>
          <p className="text-xs text-ink-muted max-w-md mx-auto font-sans">
            No agent has successfully merged approved changes to <code className="font-mono">{filePath}</code> on record.
            If an agent modified this file without an approved plan, it was flagged as a scope violation and blocked.
          </p>
          <div className="pt-2">
            <Link
              href="/ledger"
              className="text-xs font-mono text-ink underline hover:text-oxblood"
            >
              ← Back to Warrant Ledger
            </Link>
          </div>
        </div>
      ) : (
        <div className="border border-rule divide-y divide-rule bg-paper">
          <div className="px-4 py-2 bg-paper-dark/30 text-[11px] font-mono uppercase text-ink-muted flex items-center justify-between">
            <span>Authorization Records ({records.length})</span>
            <span>Switch Room Link</span>
          </div>

          {records.map((rec) => (
            <div key={rec.id} className="p-5 space-y-3 text-xs font-mono">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Link
                    href={`/w/${rec.warrant_id}`}
                    className="font-bold text-sm text-oxblood underline hover:opacity-80"
                  >
                    {rec.warrant_id}
                  </Link>
                  <span className="px-2 py-0.5 text-[10px] font-bold text-verified bg-verified-faint border border-verified/30 rounded-[1px]">
                    {rec.status}
                  </span>
                </div>

                <div className="text-[11px] text-ink-muted">
                  Merged on {new Date(rec.at).toLocaleString()}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-sans">
                <div>
                  <span className="text-[10px] font-mono text-ink-muted uppercase">Authorized Human</span>
                  <div className="font-semibold text-ink text-sm">
                    @{rec.approved_by || "unknown"}
                  </div>
                </div>

                <div>
                  <span className="text-[10px] font-mono text-ink-muted uppercase">Commit SHA</span>
                  <div className="font-mono text-xs text-ink">
                    {rec.commit_sha ? (
                      <span className="bg-paper-dark/40 px-1 py-0.5 border border-rule/50">
                        {rec.commit_sha}
                      </span>
                    ) : (
                      "unrecorded"
                    )}
                  </div>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-mono text-ink-muted uppercase">
                  Human Authorization Excerpt
                </span>
                <blockquote className="mt-1 p-3 bg-paper-light border-l-2 border-oxblood font-mono text-xs text-ink leading-relaxed">
                  {rec.excerpt || "Authorized in Switch room"}
                </blockquote>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
