"use client";

import React, { useEffect, useState } from "react";
import { SettingsResponse } from "@/types";
import { fetchSettings, seedDatabase } from "@/lib/api";

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [seedMessage, setSeedMessage] = useState<string>("");

  const loadSettings = async () => {
    setIsLoading(true);
    const data = await fetchSettings();
    setSettings(data);
    setIsLoading(false);
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleSeed = async () => {
    setSeedMessage("Seeding demo records W-014 and W-015...");
    await seedDatabase();
    await loadSettings();
    setSeedMessage("Demonstration records successfully re-seeded.");
    setTimeout(() => setSeedMessage(""), 4000);
  };

  if (isLoading || !settings) {
    return (
      <div className="py-20 text-center font-mono text-xs text-ink-muted">
        Loading system configuration...
      </div>
    );
  }

  return (
    <div className="space-y-10 max-w-4xl">
      {/* Title */}
      <div className="pb-4 hairline-b">
        <span className="text-[11px] font-mono uppercase tracking-widest text-ink-muted">
          System Administration
        </span>
        <h1 className="text-3xl font-serif font-black tracking-tight text-ink mt-1">
          Configuration & Provenance Settings
        </h1>
        <p className="text-xs text-ink-muted mt-1 font-sans">
          Runtime configuration for approver allowlists, GitHub commit status dispatch, and Switch bridge connections.
        </p>
      </div>

      {seedMessage && (
        <div className="p-3 bg-verified-faint border border-verified/50 text-verified font-mono text-xs font-semibold">
          ✓ {seedMessage}
        </div>
      )}

      {/* Grid of config sections */}
      <div className="space-y-8 text-sm">
        {/* 1. Approver Allowlist */}
        <section className="border border-rule bg-paper-card p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 hairline-b">
            <div>
              <h2 className="font-serif font-bold text-lg text-ink">
                Approver Identity Allowlist
              </h2>
              <p className="text-xs text-ink-muted font-sans mt-0.5">
                Only users matching this allowlist can approve plans (<code className="font-mono">approve W-XXX &lt;hash&gt;</code>) or merges.
              </p>
            </div>
            <span className="px-2 py-0.5 text-[10px] font-mono font-bold uppercase bg-paper-dark/60 text-ink border border-rule">
              {settings.approver_allowlist.length} Approvers
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
            {settings.approver_allowlist.map((approver) => (
              <span
                key={approver}
                className="px-3 py-1 bg-paper border border-rule/80 text-ink font-semibold rounded-[1px]"
              >
                @{approver}
              </span>
            ))}
          </div>

          <div className="text-xs font-mono text-ink-muted pt-2 hairline-t flex items-center justify-between">
            <span>Passphrase fallback enforcement:</span>
            <span className={`font-bold ${settings.passphrase_configured ? "text-verified" : "text-ink-muted"}`}>
              {settings.passphrase_configured ? "Active (APPROVER_PASSPHRASE set)" : "Inactive (allowlist matching active)"}
            </span>
          </div>
        </section>

        {/* 2. GitHub Status Configuration */}
        <section className="border border-rule bg-paper-card p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 hairline-b">
            <div>
              <h2 className="font-serif font-bold text-lg text-ink">
                GitHub Commit Status Gate
              </h2>
              <p className="text-xs text-ink-muted font-sans mt-0.5">
                Clerk posts commit statuses (<code className="font-mono">POST /repos/:owner/:repo/statuses/:sha</code>) to block PRs on scope violations.
              </p>
            </div>
            <span
              className={`px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded-[1px] ${
                settings.github.is_configured
                  ? "bg-verified-faint text-verified border border-verified/40"
                  : "bg-paper-dark text-ink-muted border border-rule"
              }`}
            >
              {settings.github.is_configured ? "Configured" : "Unconfigured (Local Mode)"}
            </span>
          </div>

          <div className="font-mono text-xs space-y-2 bg-paper p-4 border border-rule/70">
            <div className="flex items-center justify-between">
              <span className="text-ink-muted">Target Repository:</span>
              <span className="font-semibold text-ink">{settings.github.repo || "None configured"}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-ink-muted">Integration State:</span>
              <span className="text-ink">{settings.github.status_message}</span>
            </div>
          </div>

          <p className="text-xs font-sans text-ink-muted pt-2 hairline-t">
            If GITHUB_TOKEN is omitted in .env, Warrant runs safely in local mode without failing.
          </p>
        </section>

        {/* 3. Switch Room Bridge */}
        <section className="border border-rule bg-paper-card p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 hairline-b">
            <div>
              <h2 className="font-serif font-bold text-lg text-ink">
                Switch Collaboration Bridge
              </h2>
              <p className="text-xs text-ink-muted font-sans mt-0.5">
                Switch rooms bridge chat platforms (Slack, Teams, Discord, Mattermost) to provide shared history evidence.
              </p>
            </div>
            <span className="px-2 py-0.5 text-[10px] font-mono font-bold uppercase bg-verified-faint text-verified border border-verified/40 rounded-[1px]">
              Protocol Ready
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 font-mono text-xs">
            <div className="border border-rule/70 p-3 bg-paper">
              <span className="text-[10px] text-ink-muted uppercase block">Switch Server URL</span>
              <span className="font-semibold text-ink text-xs mt-1 block">{settings.switch.server_url}</span>
            </div>
            <div className="border border-rule/70 p-3 bg-paper">
              <span className="text-[10px] text-ink-muted uppercase block">Room Channel</span>
              <span className="font-semibold text-ink text-xs mt-1 block">{settings.switch.room_id}</span>
            </div>
          </div>
        </section>

        {/* 4. Real vs Seeded Data Audit Panel */}
        <section className="border border-rule bg-paper-light p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 hairline-b">
            <div>
              <h2 className="font-serif font-bold text-lg text-ink">
                Real vs. Seeded Demo Data Audit
              </h2>
              <p className="text-xs text-ink-muted font-sans mt-0.5">
                Honesty principle: No invented metrics. Any seeded records are explicitly labelled in the ledger.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 font-mono text-xs">
            <div className="border border-rule p-4 bg-paper">
              <div className="text-[10px] text-ink-muted uppercase">Live Production Records</div>
              <div className="text-2xl font-serif font-black text-ink mt-1">
                {settings.data_sources.live_records}
              </div>
              <p className="text-[11px] text-ink-muted font-sans mt-1">
                Generated from real Switch room events and live git commits.
              </p>
            </div>

            <div className="border border-rule p-4 bg-paper">
              <div className="text-[10px] text-ink-muted uppercase">Seeded Demonstration Records</div>
              <div className="text-2xl font-serif font-black text-oxblood mt-1">
                {settings.data_sources.seeded_records}
              </div>
              <p className="text-[11px] text-ink-muted font-sans mt-1">
                W-014 (clean invoice tax fix) & W-015 (payments scope violation).
              </p>
            </div>
          </div>

          <div className="pt-2 flex items-center justify-between">
            <span className="text-xs font-mono text-ink-muted">Need fresh demo fixtures?</span>
            <button
              onClick={handleSeed}
              className="px-4 py-1.5 bg-ink text-paper text-xs font-mono uppercase tracking-wider font-semibold rounded-[1px] hover:bg-oxblood transition-colors"
            >
              Re-Seed Demo Fixtures (W-014 & W-015)
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
