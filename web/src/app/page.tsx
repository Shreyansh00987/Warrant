import React from "react";
import Link from "next/link";
import { fetchWarrants, fetchStats } from "@/lib/api";
import { WarrantCard } from "@/components/WarrantCard";
import { ChatExcerptBlame } from "@/components/ChatExcerptBlame";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const warrants = await fetchWarrants();
  const stats = await fetchStats();

  // Find hero warrant (prefer W-014 or first available)
  const heroWarrant = warrants.find((w) => w.id === "W-014") || warrants[0];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="space-y-6 pt-4 pb-8 max-w-3xl">
        <div className="inline-flex items-center gap-2 px-2 py-0.5 border border-rule text-[11px] font-mono uppercase tracking-widest text-ink-muted bg-paper-light">
          <span>The Switch Ledger Protocol</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-serif font-black tracking-tight leading-[1.08] text-ink">
          Every agent-made change, traced to the human who said yes.
        </h1>

        <p className="text-base sm:text-lg text-ink-muted font-sans leading-relaxed">
          Teams let autonomous coding agents modify codebases, but authorization lives in scattered
          chat threads and private terminal sessions. A PR approval only says someone approved a diff—it
          doesn't prove the agent stayed within authorized scope.
        </p>

        <div className="flex flex-wrap items-center gap-4 pt-2">
          <Link
            href="/ledger"
            className="px-5 py-2.5 bg-ink text-paper font-mono text-xs uppercase tracking-wider font-semibold hover:bg-oxblood transition-colors rounded-[1px]"
          >
            Open Ledger ({stats.total} Records) →
          </Link>
          <Link
            href="/w/W-015"
            className="px-4 py-2.5 border border-rule hover:border-ink font-mono text-xs text-ink transition-colors rounded-[1px]"
          >
            View Scope Drift Demo (W-015)
          </Link>
        </div>
      </section>

      {/* Hero Warrant Card */}
      {heroWarrant && (
        <section className="space-y-3">
          <div className="flex items-center justify-between text-xs font-mono text-ink-muted">
            <span>Verified Exemplar Record</span>
            <span className="font-semibold text-ink">Hash-Linked Ledger Evidence</span>
          </div>
          <WarrantCard warrant={heroWarrant} showLinks={true} />
        </section>
      )}

      {/* Code Blame vs Chat Excerpt Section */}
      <section className="space-y-3">
        <ChatExcerptBlame />
      </section>

      {/* How It Works: The Two Gates */}
      <section className="space-y-8 pt-8 hairline-t">
        <div className="max-w-2xl">
          <span className="text-[11px] font-mono uppercase tracking-widest text-ink-muted">
            Deterministic Integrity
          </span>
          <h2 className="text-2xl sm:text-3xl font-serif font-bold text-ink mt-1">
            How Warrant Enforces Agent Scope
          </h2>
          <p className="text-sm text-ink-muted mt-2">
            Clerk is a deterministic Python gatekeeper, not an LLM. It parses typed Switch chat commands,
            verifies approver allowlists, computes SHA-256 hashes, and sets GitHub commit statuses.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
          <div className="border border-rule p-5 bg-paper-light">
            <div className="font-mono text-xs font-bold text-oxblood uppercase tracking-wider mb-2">
              Gate 1 · Plan Binding
            </div>
            <h3 className="font-serif font-bold text-lg text-ink mb-1">
              Approval Bound to Plan Hash
            </h3>
            <p className="text-xs text-ink-muted font-sans leading-relaxed">
              The Builder (Claude Code) emits a planned file list and a SHA-256 hash. The human approves
              with <code className="font-mono text-ink bg-paper-dark/40 px-1">approve W-014 a3f9c2</code>.
              A plan that mutates after approval cannot be accidentally approved.
            </p>
          </div>

          <div className="border border-rule p-5 bg-paper-light">
            <div className="font-mono text-xs font-bold text-oxblood uppercase tracking-wider mb-2">
              Gate 2 · Scope Enforcer
            </div>
            <h3 className="font-serif font-bold text-lg text-ink mb-1">
              Deterministic Scope Check
            </h3>
            <p className="text-xs text-ink-muted font-sans leading-relaxed">
              When the build reports its git diff, Clerk performs a mathematical set check:
              <span className="block font-mono text-[11px] text-ink my-1 font-semibold">TouchedFiles ⊆ PlannedFiles</span>
              If the agent touches any unauthorized file (e.g. <code className="font-mono text-oxblood">payments/</code>),
              status instantly fails to <span className="text-oxblood font-semibold">OUT OF SCOPE</span>.
            </p>
          </div>

          <div className="border border-rule p-5 bg-paper-light">
            <div className="font-mono text-xs font-bold text-oxblood uppercase tracking-wider mb-2">
              Independent Audit
            </div>
            <h3 className="font-serif font-bold text-lg text-ink mb-1">
              Multi-Provider Review
            </h3>
            <p className="text-xs text-ink-muted font-sans leading-relaxed">
              A second, independent agent provider (Codex or OpenCode) verifies tests and diff semantics.
              Only when Scope is CLEAN and Auditor passes can the human issue
              <code className="font-mono text-ink bg-paper-dark/40 px-1 ml-1">merge W-014</code>.
            </p>
          </div>
        </div>
      </section>

      {/* Terminal Verification Banner */}
      <section className="border border-rule p-6 bg-paper-dark/20 text-xs font-mono space-y-3">
        <div className="flex items-center justify-between">
          <span className="font-bold text-ink uppercase tracking-wider">
            Standalone CLI Verification
          </span>
          <span className="text-ink-muted">warrant verify &lt;commit-sha&gt;</span>
        </div>
        <p className="text-ink-muted font-sans text-xs">
          Judges and engineers can verify any commit SHA directly from the terminal without opening a browser.
          The CLI recomputes the SHA-256 chain and catches any tampered records.
        </p>
        <div className="p-3 bg-paper border border-rule/80 font-mono text-xs text-ink">
          <code>python warrant.py verify 8f4a12c4b1239840294104928172635418294021</code>
        </div>
      </section>
    </div>
  );
}
