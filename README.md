# Warrant

> **Every agent-made change, traced to the human who said yes.**

A deterministic scope gatekeeper and hash-linked authorization ledger for autonomous coding agents, powered by **Switch** multi-agent rooms.

Built for the **Flip the Switch Hackathon 2026** (WeMakeDevs × DevTools Academy × Switch).

**Live Cloud Deployment**:
- 🌐 **Web UI Ledger**: [https://warrant-web-ncno.onrender.com](https://warrant-web-ncno.onrender.com)
- ⚙️ **Clerk API**: [https://warrant-clerk.onrender.com](https://warrant-clerk.onrender.com)
- 📖 **API Docs (Swagger)**: [https://warrant-clerk.onrender.com/docs](https://warrant-clerk.onrender.com/docs)
- 📰 **DEV.to Article**: [Building Warrant on DEV.to](https://dev.to/shreyansh_agrahari_2009db/building-warrant-every-agent-made-change-traced-to-the-human-who-said-yes-dco)
- 🎬 **1-Minute Demo Video**: [Watch Demo Video](https://github.com/Shreyansh00987/Warrant/raw/main/video/warrant_demo_video.mp4)
- 📦 **GitHub Repository**: [https://github.com/Shreyansh00987/Warrant](https://github.com/Shreyansh00987/Warrant)

---

## 30-Second Pitch: Why Switch is Central

Modern engineering teams let autonomous coding agents (Claude Code, Codex, OpenCode) refactor and write production code. But authorization currently lives in private terminal sessions and scattered chat channels. A GitHub PR approval only confirms someone approved a diff—it does not link the diff to the authorized intent, nor does it guarantee the agent stayed within approved scope.

**Warrant binds the entire lifecycle into a verifiable hash-linked record**:
1. The human's request in the shared Switch room.
2. The Builder agent's proposed plan, bound to a SHA-256 plan hash.
3. The human's typed approval of that exact plan hash.
4. The deterministic scope check ($$\text{TouchedFiles} \subseteq \text{PlannedFiles}$$).
5. The independent Auditor agent's verdict.
6. The resulting commit status on GitHub.

**Without Switch's shared room, there is no shared evidence, no multi-agent collaboration, and no warrant.**

---

## Architecture

```
   +-----------------------------------------------------------------------------------+
   |                                 SWITCH ROOM                                      |
   |                                                                                   |
   |   [Human Developer]           [Builder Agent]             [Auditor Agent]        |
   |   (e.g., Priya)              (Claude Code)               (Codex / OpenCode)      |
   |         |                           |                            |                |
   |         | 1. Request Task           |                            |                |
   |         +-------------------------->|                            |                |
   |         |                           | 2. Post Plan + Plan Hash   |                |
   |         |<--------------------------+                            |                |
   |         |                           |                            |                |
   |         | 3. "approve W-014 a3f9c2" |                            |                |
   |         +---------------------------+--------------------------->|                |
   |                                                                  |                |
   +---------------------------------------+--------------------------+----------------+
                                           | Event Stream (HTTP + SSE)
                                           v
   +-----------------------------------------------------------------------------------+
   |                                WARRANT CLERK                                      |
   |   (Deterministic Python FastAPI Enforcer - Not an LLM)                           |
   |                                                                                   |
   |   1. Approver Verification (Allowlist + optional Passphrase)                     |
   |   2. Plan Hash Matching & Binding                                                |
   |   3. Deterministic Scope Check (Approved File List vs Git Diff File List)         |
   |   4. Hash Chain Ledger (`prev_hash` -> `record_hash`)                             |
   |   5. GitHub Commit Status Dispatch (`pending` / `success` / `failure`)            |
   +---------------------------------------+-------------------------------------------+
                                           | REST API
                     +---------------------+---------------------+
                     v                                           v
   +-----------------------------------+       +-----------------------------------+
   |         WARRANT LEDGER UI         |       |        WARRANT VERIFY CLI         |
   |   Next.js App Router + Tailwind   |       |   Deterministic Terminal Tool     |
   |   Paper/Ink Minimal Skeuomorphic  |       |   `python warrant.py verify <sha>`|
   |   Stamp & Provenance Explorer     |       |   Recomputes hash chain & diff    |
   +-----------------------------------+       +-----------------------------------+
```

---

## The Switch Room Transcript

Here is how the collaboration unfolds inside the Switch room:

```text
[PRIYA]
Priya: @claude-code fix invoice tax calculation for non-taxable items. See issue #104. (W-014)

[BUILDER - Claude Code]
Claude Code: Plan for W-014
### Proposed Changes
- In `src/invoice/calculator.py`: Add an exemption check in `calculate_tax()` before applying VAT.
- In `tests/test_calculator.py`: Add test cases for tax-exempt line items.
### Target Files
- `src/invoice/calculator.py`
- `tests/test_calculator.py`
Plan hash: eb4d3b21131d08cb29f01da5fd0a63d6d6aeaedac5c9e9f49ec13d7e45311f60
Awaiting typed human approval: approve W-014 eb4d3b

[PRIYA]
Priya: approve W-014 eb4d3b

[CLERK]
Clerk: Plan eb4d3b approved by @priya. Warrant W-014 status: APPROVED_PLAN. Proceed with implementation.

[BUILDER - Claude Code]
Claude Code: built W-014 branch=fix/invoice-tax-exempt commit=8f4a12c4b1239840294104928172635418294021 diff=...

[CLERK]
Clerk: Deterministic Scope Check Passed: 2 touched files strictly authorized in approved plan. GitHub commit status: PENDING.

[AUDITOR - Codex]
Codex: audit W-014 pass Unit tests pass (18/18). Math verified. Zero regressions.

[PRIYA]
Priya: merge W-014

[CLERK]
Clerk: Warrant W-014 VERIFIED. Record hash linked: 838765aa... GitHub commit status set to SUCCESS.
```

---

## Real vs. Staged vs. Not Implemented

| Capability | Status | Notes |
|---|---|---|
| **Deterministic Scope Enforcer** | **REAL** | Pure Python set arithmetic in `clerk/scope.py`. Checks `TouchedFiles ⊆ PlannedFiles`. Zero LLM hallucinations. |
| **Plan Hash Binding Gate** | **REAL** | Normalized SHA-256 plan hashing in `clerk/hasher.py`. Typed approval verifies prefix match before authorizing. |
| **Hash-Linked Ledger** | **REAL** | `prev_hash` links to `record_hash` across all warrants in SQLite. Recomputed and validated on every query. |
| **Standalone Verify CLI** | **REAL** | `python warrant.py verify <sha>` recomputes hashes and catches tampered records with `--tamper`. |
| **Ledger Web UI** | **REAL** | Next.js 15 App Router + Tailwind CSS with paper/ink tokens, skeuomorphic Stamp press animation, WarrantCard, and all 5 screens. |
| **Approver Allowlist & Passphrase** | **REAL** | Verified against `APPROVER_ALLOWLIST` in `clerk/service.py`. Fails closed if unauthorized. |
| **GitHub Commit Status Dispatch** | **REAL** | Dispatches to GitHub REST API if `GITHUB_TOKEN` is set; gracefully skips in local mode. |
| **Switch Room Template (YAML)** | **REAL** | Follows the official Switch template schema (`switch/agent-templates/warrant-room.template.yaml`). |
| **Switch Agent Protocol Client** | **REAL** | `clerk/switch_client.py` connects to Switch HTTP + SSE stream. |
| **Replay Event Fixtures** | **REAL** | `switch/replay.py` replays captured pass and drift conversations turn-by-turn. |
| **Target Billing Service (`demo-repo/`)** | **STAGED** | Small service with invoice calculator and restricted payments module created as a demo testbed. |
| **Sample Tasks (W-014 & W-015)** | **STAGED** | Realistic bugfix and drift scenarios used to demo the clean path and drift detection. |
| **Interactive Chat Buttons** | **NOT IMPLEMENTED** | Deliberately omitted. Switch multi-platform bridges do not guarantee interactive button rendering; Warrant strictly uses typed commands. |
| **Line-Level AST Provenance** | **OUT OF SCOPE** | Warrant tracks file-level diff provenance. Line-level AST tracing was excluded by specification. |
| **Trustless ed25519 Signing** | **OUT OF SCOPE** | Warrant is a SHA-256 hash-linked audit ledger. It does not implement asymmetric PKI signing. |

---

## Quickstart & Demo Commands

### Option A: Local Development (Recommended)

1. **Install Python & Node Dependencies**:
   ```bash
   pip install -r requirements.txt
   cd web && npm install && cd ..
   ```

2. **Seed the Database with Demo Records**:
   ```bash
   python warrant.py seed
   ```

3. **Start the Clerk API Server**:
   ```bash
   python warrant.py serve --port 8000
   ```

4. **Start the Ledger Web UI** (in a second terminal):
   ```bash
   cd web && npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) in your browser.

5. **Run CLI Verification**:
   ```bash
   # Verify the clean commit (W-014):
   python warrant.py verify 8f4a12c4b1239840294104928172635418294021

   # Verify the drift commit (W-015, fails scope check):
   python warrant.py verify e39a58b291049102948201948201948201948201

   # Demonstrate tamper detection (modifies a byte in memory):
   python warrant.py verify 8f4a12c4b1239840294104928172635418294021 --tamper
   ```

6. **Replay Real Switch Room Event Streams**:
   ```bash
   # Replay the clean run (W-014):
   python warrant.py replay switch/fixtures/pass_run.json

   # Replay the drift attempt (W-015, blocked by Clerk):
   python warrant.py replay switch/fixtures/drift_run.json
   ```

7. **Run the Test Suite**:
   ```bash
   python -m pytest -v
   ```

---

### Option B: Docker Compose

If Docker is installed on your workstation:
```bash
docker compose up --build
```
- Ledger UI: [http://localhost:3000](http://localhost:3000)
- Clerk API: [http://localhost:8000](http://localhost:8000)

---

## The 5 Screens Built
1. **Landing (`/`)**: High-impact value proposition, hero WarrantCard, and interactive line-by-line git blame view linking changed code to the exact Switch chat excerpt.
2. **Ledger (`/ledger`)**: Dense, tabular overview of all warrants, status counters, source filters, and full keyboard navigation (`j`/`k`/`Enter`/`Esc`).
3. **Warrant Detail (`/w/[id]`)**: The skeuomorphic paper card with animated rubber stamp, horizontal workflow pipeline, deterministic scope inspector, hash chain cryptographic proof, and immutable chat timeline.
4. **File Provenance (`/files/[...path]`)**: Pick any changed file (e.g. `src/invoice/calculator.py` or `src/payments/stripe_gateway.py`) to see every warrant that touched it and the originating chat excerpt.
5. **Settings & Config (`/settings`)**: Live approver allowlist, GitHub commit status state, Switch room mapping, and transparent Real vs Seeded data audit.

---

## Known Limitations & Honest Trade-offs
1. **Hash-Linked, Not Byzantine Trustless**: A compromised Clerk server could forge records in its own SQLite database. Warrant provides verifiable audit trails for trusted teams, not decentralized consensus.
2. **Sender Display Names**: Chat bridges vary in whether they guarantee authenticated user IDs. To harden against username spoofing, configure `APPROVER_PASSPHRASE` in `.env`.
3. **File-Level Granularity**: Scope checking operates on file paths (`TouchedFiles ⊆ PlannedFiles`). Hunk-level or AST-level statement scoping is future work.

---

## Licenses & Third-Party Credits
- **Switch**: Apache License 2.0 with the Commons Clause ([sandbox-quantum/switch](https://github.com/sandbox-quantum/switch)).
- **Warrant**: Licensed under the [Apache License 2.0](LICENSE).
