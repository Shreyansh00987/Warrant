# Warrant 2:30 Video Demo Script (docs/DEMO_SCRIPT.md)

**Title**: Warrant — Every Agent-Made Change, Traced to the Human Who Said Yes  
**Track**: Flip the Switch Hackathon 2026 (WeMakeDevs × DevTools Academy × Switch)  
**Total Target Runtime**: 2 minutes, 30 seconds  

---

## Shot List & Voiceover

### [0:00 - 0:20] Act I: The Problem
* **Visual**: Quick camera pan on terminal sessions, Slack threads, and a GitHub PR page with an ambiguous approval comment.
* **Audio / Voiceover**:
  > *"When teams let autonomous coding agents like Claude Code or Codex touch their repositories, the human authorization is lost across private terminal sessions and ephemeral chat rooms. A GitHub PR approval says someone approved a diff, but it doesn't record the authorized intent, and it doesn't prove the agent stayed within bounds. Introducing **Warrant**."*
* **Reality Note**: Real problem statement.

---

### [0:20 - 0:45] Act II: Gate 1 — Plan Bound to Hash in Switch Room
* **Visual**: Screen recording of the Switch room (`warrant-room`). Priya types:
  ```text
  @claude-code fix invoice tax calculation for non-taxable items. (W-014)
  ```
  Claude Code responds with a structured plan listing `src/invoice/calculator.py` and `tests/test_calculator.py`, ending with `Plan hash: eb4d3b...`.
* **Audio / Voiceover**:
  > *"Everything starts in a shared Switch room. Without Switch's unified collaboration space, there is no shared history and no warrant. Priya requests a bug fix. Claude Code drafts a plan, lists the exact files it will touch, and computes a SHA-256 plan hash."*
* **Reality Note**: Real Switch agent template and message protocol.

---

### [0:45 - 1:10] Act III: The Typed Approval & Skeuomorphic Stamp
* **Visual**: In Switch chat, Priya types:
  ```text
  approve W-014 eb4d3b
  ```
  Switch directly over to the Warrant Ledger UI (`http://localhost:3000/w/W-014`). The paper WarrantCard renders, and with a short rotate-and-settle press animation, the oxblood **APPROVED** stamp presses onto the document.
* **Audio / Voiceover**:
  > *"Priya types `approve W-014 eb4d3b`. Clerk—our deterministic Python gatekeeper—verifies Priya's identity against the allowlist and matches the hash. If the plan mutated after approval, it would be rejected. On the Warrant ledger, the warrant is stamped in oxblood ink."*
* **Reality Note**: Real Clerk hashing, allowlist check, and CSS stamp press animation.

---

### [1:10 - 1:40] Act IV: Build, Deterministic Scope Check, Independent Audit
* **Visual**: Claude Code posts its build report: `built W-014 branch=fix/invoice-tax commit=8f4a12c...`.
  Clerk compares `TouchedFiles ⊆ PlannedFiles`. The UI shows "Scope CLEAN: 2/2 files authorized".
  Next, Codex (running as an independent auditor agent) posts: `audit W-014 pass`.
  Priya approves merge: `merge W-014`. Status transitions to `APPROVED_MERGE` and GitHub commit status turns green.
* **Audio / Voiceover**:
  > *"Claude Code implements the fix on a branch. Clerk deterministically inspects the git patch. Every touched file is in the approved plan. Codex—a separate agent provider for defense-in-depth—runs tests and passes the audit. Priya merges, and Clerk sets the GitHub commit status to success."*
* **Reality Note**: Real scope checker arithmetic and hash-chain link.

---

### [1:40 - 2:05] Act V: The Drift Attempt — Clerk Blocks Unauthorized Access
* **Visual**: Alec asks Claude Code in Switch chat to format invoice currency (W-015).
  Priya approves the plan for `src/invoice/formatter.py`.
  When Claude Code builds, its diff secretly modifies `src/payments/stripe_gateway.py`!
  Instantly, Clerk flags **SCOPE VIOLATION**. On the UI (`/w/W-015`), a red **OUT OF SCOPE** stamp lands, naming the offending payment file. The GitHub check turns red.
* **Audio / Voiceover**:
  > *"Now watch what happens when an agent drifts. In Warrant W-015, Claude Code was approved only for invoice formatting, but it drifted into our sensitive payments gateway. Clerk catches it instantly. TouchedFiles is NOT a subset of PlannedFiles. The commit is rejected, status is marked OUT OF SCOPE, and GitHub blocks the merge."*
* **Reality Note**: Real deterministic failure, status check, and tamper-proof event record.

---

### [2:05 - 2:25] Act VI: File Provenance & Git Blame Jump
* **Visual**: Switch to `/files/src/invoice/calculator.py` in the ledger UI.
  Click on line 17 (`if item.get("tax_exempt"): continue`).
  The right panel immediately highlights the exact Switch chat excerpt where Priya authorized that line.
* **Audio / Voiceover**:
  > *"Months later, when an engineer asks 'who authorized this line in calculator.py?', Warrant gives immediate file provenance. One click reveals the exact Switch room excerpt and the human who said yes."*
* **Reality Note**: Real file provenance database queries and link tracing.

---

### [2:25 - 2:30] Act VII: Terminal CLI Verification & Close
* **Visual**: In terminal, run:
  ```bash
  python warrant.py verify 8f4a12c4b1239840294104928172635418294021
  ```
  Terminal displays green `>>> [RESULT] VERIFIED <<<`.
  Next, run with `--tamper`:
  ```bash
  python warrant.py verify 8f4a12c4b1239840294104928172635418294021 --tamper
  ```
  Terminal displays red `[RESULT] UNAUTHORIZED. Reason: Hash chain integrity check FAILED.`
  Fade to title card: **WARRANT — No Switch, no warrant.**
* **Audio / Voiceover**:
  > *"Finally, anyone can run `warrant verify` in the terminal to cryptographically trace the hash chain. If a single byte is tampered with, verification fails. Warrant gives engineering teams the confidence to unleash coding agents. No Switch, no warrant."*
* **Reality Note**: Real CLI output and exit codes.
