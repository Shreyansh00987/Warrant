# Warrant Architecture (docs/ARCHITECTURE.md)

## 1. Overview & Problem Statement

Modern development workflows increasingly delegate code generation and refactoring to autonomous AI coding agents (Claude Code, OpenAI Codex, OpenCode). However, authorization for agent tasks is currently fragmented across private terminal sessions, ephemeral Slack/Discord channels, and unverified PR comments.

When an outage or security vulnerability occurs, teams cannot answer:
1. **Who authorized this agent to make this specific change?**
2. **What exact plan was presented when the human said yes?**
3. **Did the agent stay strictly within the promised scope, or did it touch unauthorized files?**
4. **Did an independent review verify the build before merge?**

A GitHub PR approval only confirms that a human approved a final diff—it does not link the diff to the authorized intent, nor does it guarantee the agent didn't drift outside its approved scope.

**Warrant** solves this by establishing a **hash-linked ledger** where every agent-made change is bound to the human who said yes, validated through an independent multi-agent room powered by **Switch**.

---

## 2. System Architecture

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
                                           | Event Stream (SSE / Webhook)
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
   |   Paper/Ink Minimal Skeuomorphic  |       |   `warrant verify <sha>`          |
   |   Stamp & Provenance Explorer     |       |   Recomputes hash chain & diff    |
   +-----------------------------------+       +-----------------------------------+
```

---

## 3. The Warrant Lifecycle & Two Gates

### Gate 1: Plan Approval (Pre-Code)
1. **Task Request**: A human team member (e.g. `priya`) asks the Builder agent to perform a task in the Switch room.
2. **Plan Emission**: The Builder drafts a structured plan specifying:
   - Summary of change.
   - Exact list of files to be modified/created (`target_files`).
   - The SHA-256 hash of the normalized plan (`plan_hash`).
3. **Approval**: An authorized approver types:
   ```text
   approve W-014 a3f9c2
   ```
4. **Clerk Ingestion**: Clerk verifies:
   - Is the sender allowlisted in `APPROVER_ALLOWLIST`?
   - Does the provided hash prefix match the SHA-256 hash of the pending plan?
   - If valid, Clerk creates/updates the warrant record with status `APPROVED_PLAN` and posts confirmation to the room.

### Gate 2: Scope & Audit Gate (Post-Code)
1. **Build & Branch**: The Builder executes the work on a git branch and posts the branch name and commit SHA (`commit_sha`).
2. **Deterministic Scope Check (Clerk)**:
   - Clerk inspects the actual `git diff` between the branch and base.
   - Clerk extracts every touched file path.
   - **Scope Check Rule**:
     $$\text{TouchedFiles} \subseteq \text{PlanFiles}$$
   - If any touched file is not in `PlanFiles` (e.g. agent modified `payments/` when only authorized for `invoice/`):
     $$\text{Result} = \text{SCOPE\_VIOLATION} \implies \text{Commit Status} = \text{failure}$$
3. **Auditor Review**:
   - An independent agent runtime (e.g., Codex or OpenCode) inspects the diff and test results.
   - Auditor posts its verdict (`PASS` or `BLOCK`) with technical notes.
4. **Merge Approval**:
   - Approver types `merge W-014`.
   - Clerk only permits merge if Scope Check is `CLEAN` and Auditor verdict is `PASS`.
   - Commit status on GitHub is updated to `success`.

---

## 4. Hash Chain & Data Integrity Spec

Warrant maintains a tamper-evident hash-linked ledger.

### A. Plan Hash
$$\text{plan\_hash} = \text{SHA256}(\text{normalized}(\text{plan\_markdown}))$$
Normalized: UTF-8 encoded with normalized CRLF to LF, trimmed leading/trailing whitespace.

### B. Diff Hash
$$\text{diff\_hash} = \text{SHA256}(\text{git\_patch\_content})$$

### C. Record Hash
Each warrant record $i$ is linked to the previous warrant $i-1$:
$$\text{record\_hash}_i = \text{SHA256}(\text{prev\_hash} \parallel \text{id} \parallel \text{plan\_hash} \parallel \text{diff\_hash} \parallel \text{scope\_result} \parallel \text{approved\_by} \parallel \text{status})$$

### D. Verification (`warrant verify <sha>`)
The standalone CLI tool `warrant verify`:
1. Fetches the record for `<commit-sha>`.
2. Verifies the hash link to the previous record.
3. Re-calculates the plan hash from stored markdown.
4. Re-calculates the diff hash from the git commit.
5. Re-executes the deterministic scope check.
6. Returns `VERIFIED` with full proof chain, or `UNAUTHORIZED` with the offending diff/tamper reason.

---

## 5. Security & Fail-Closed Guarantee

1. **Deterministic Enforcer**: Clerk is written in Python with no LLM in its critical path. It never hallucinates approvals or skips checks.
2. **Fail-Closed Default**: If Clerk crashes, cannot parse an approval, or encounters an unrecognized sender, the commit status remains `pending` and cannot merge.
3. **Immutability of Evidence**: Raw chat excerpts and message IDs from the Switch room are stored inside the SQLite ledger so evidence persists even if chat channels are pruned or edited.
4. **Clear Attribution**: Every warrant lists `approved_by`, `approved_msg_id`, and `approved_at`.
