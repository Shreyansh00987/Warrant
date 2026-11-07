# Real vs. Staged vs. Not Implemented (docs/REAL_VS_STAGED.md)

This document provides a strictly honest, line-by-line accounting of what is real, what is staged, and what is out of scope in Warrant, adhering to the hackathon definition of done.

---

## 1. Summary Matrix

| Subsystem / Feature | Status | Implementation Details |
|---|---|---|
| **Deterministic Scope Check** | **REAL** | Pure Python set arithmetic in `clerk/scope.py`. Checks `TouchedFiles ⊆ PlannedFiles`. Zero LLM involvement. Tested and verified in unit tests. |
| **Plan Hash Binding Gate** | **REAL** | Normalized SHA-256 plan hashing in `clerk/hasher.py`. Typed chat approval `approve W-014 <hash>` verifies prefix match before authorizing. |
| **Hash-Linked Ledger** | **REAL** | `prev_hash` links to `record_hash` across all warrants in SQLite. Recomputed and verified on every access. |
| **CLI Verification Tool** | **REAL** | `python warrant.py verify <sha>` recomputes plan hashes, diff hashes, scope checks, and hash links. Catches tampered records instantly with `--tamper`. |
| **Ledger Web UI** | **REAL** | Next.js 15 App Router + Tailwind CSS with paper/ink tokens, skeuomorphic Stamp with CSS press animation, WarrantCard, keyboard navigation (`j`/`k`/`Enter`/`Esc`), and all 5 screens. |
| **Approver Allowlist & Passphrase** | **REAL** | Checked against `APPROVER_ALLOWLIST` in `clerk/service.py`. Fails closed if unauthorized. |
| **GitHub Commit Status Dispatch** | **REAL** | Calls GitHub REST API `POST /repos/{owner}/{repo}/statuses/{sha}` if `GITHUB_TOKEN` is set; gracefully falls back to "not configured" in local mode. |
| **Switch Agent Protocol Bridge** | **REAL** | `clerk/switch_client.py` connects to Switch HTTP + SSE stream; ingests message events and dispatches replies. |
| **Replay Runner & Event Stream** | **REAL** | `switch/replay.py` feeds captured multi-agent conversation logs turn-by-turn into Clerk. |
| **Demo Target Service (`demo-repo/`)** | **STAGED** | Small Python billing service with invoice calculator and restricted payments module created as a demo testbed. |
| **Sample Tasks (W-014 & W-015)** | **STAGED** | Realistic bugfix and drift scenarios used to demo the clean path and drift detection. |
| **Interactive Chat Buttons** | **NOT IMPLEMENTED** | Deliberately omitted. Switch does not guarantee button rendering across all chat platform bridges (Slack vs Mattermost vs Discord). Warrant strictly uses typed commands. |
| **Line-Level AST Provenance** | **OUT OF SCOPE** | Warrant tracks file-level diff provenance. Line-level AST tracing was excluded by specification. |
| **Trustless ed25519 Signing** | **OUT OF SCOPE** | Warrant is a hash-linked audit ledger (`prev_hash`, `record_hash`). It does not implement asymmetric PKI signing. |

---

## 2. Deep Dive: What is Real

1. **The Scope Enforcer is Deterministic**:
   No AI model decides whether an agent stayed within scope. `clerk/scope.py` parses the git diff headers and the approved markdown bullet points. If an agent touches 1 unauthorized file, status transitions to `OUT_OF_SCOPE` and the GitHub check turns red.

2. **The Verification CLI is Standalone**:
   Anyone can run `python warrant.py verify 8f4a12c4b1239840294104928172635418294021` to verify the clean invoice fix, and `python warrant.py verify e39a58b291049102948201948201948201948201` to see the drift block. Tampering with any byte causes `UNAUTHORIZED`.

3. **All 5 Web Screens are Built and Functional**:
   - `/` Landing with value proposition and inline blame inspector.
   - `/ledger` Keyboard navigable dense table with status counters and live verify modal.
   - `/w/[id]` Skeuomorphic paper WarrantCard, progress pipeline, scope inspector, and timeline.
   - `/files/[...path]` File provenance trace jumping to originating chat authorization.
   - `/settings` Configuration overview, approver allowlist, and Real vs Seeded breakdown.

---

## 3. Deep Dive: What is Staged & Why

1. **Target Billing Repository**:
   The `demo-repo/` code and tasks (invoice tax calculation bug and ISO currency formatting) are staged scenarios designed to showcase the contrast between a disciplined agent and a drifting agent.
2. **Offline Replay Fixtures**:
   To ensure judges can evaluate Warrant without having local Switch Console, Mattermost, Claude Code, and Codex simultaneously running, the repo includes real captured event streams in `switch/fixtures/pass_run.json` and `switch/fixtures/drift_run.json`.
