---
title: "Building Warrant: Every Agent-Made Change, Traced to the Human Who Said Yes"
published: true
tags: ai, devops, productivity, webdev
cover_image: https://raw.githubusercontent.com/Shreyansh00987/Warrant/main/video/scene2_switch_shot.png
description: "How we built Warrant for the Flip the Switch Hackathon 2026—a deterministic scope gatekeeper and hash-linked authorization ledger for autonomous coding agents."
---

> *Built for the **Flip the Switch Hackathon 2026** (WeMakeDevs × DevTools Academy × Switch) — Track: **Best Business Workflow**.*

- 🌐 **Live Web App**: [https://warrant-web-ncno.onrender.com](https://warrant-web-ncno.onrender.com)
- ⚙️ **Backend API & Swagger Docs**: [https://warrant-clerk.onrender.com/docs](https://warrant-clerk.onrender.com/docs)
- 📦 **GitHub Repository**: [https://github.com/Shreyansh00987/Warrant](https://github.com/Shreyansh00987/Warrant)
- 🎬 **1-Minute Demo Video**: [Watch on GitHub](https://github.com/Shreyansh00987/Warrant/raw/main/video/warrant_demo_video.mp4)

---

## 1. The Dilemma of Autonomous Coding Agents

Engineering teams are in a rush to adopt autonomous coding agents like **Claude Code**, **Codex**, and **OpenCode**. These agents can read a Jira issue, explore a monorepo, refactor legacy code, and open pull requests in seconds.

**But there is a glaring governance blind spot**:
*Human authorization currently lives scattered across private terminal windows and ephemeral direct messages.*

When a pull request is approved on GitHub, all anyone knows is that a reviewer stamped a final git diff. Nobody can later answer:
1. *Who authorized this agent to make this change?*
2. *What exact plan was approved?*
3. *Did the agent stay strictly inside the authorized scope, or did it sneakily drift into sensitive files (like billing or auth)?*

To solve this, we built **Warrant**.

---

## 2. The Concept: What is a Warrant?

A **warrant** is a hash-linked cryptographic record binding:
1. The human's initial request message.
2. The Builder agent's proposed plan, bound to a SHA-256 plan hash.
3. The human lead's typed approval of that exact plan hash.
4. A **deterministic scope check** ($$\text{TouchedFiles} \subseteq \text{PlannedFiles}$$).
5. An independent reviewer agent's audit verdict.
6. The resulting commit status on GitHub.

```
   [Human Lead]           [Builder Agent]             [Auditor Agent]
   (e.g., Priya)          (Claude Code)               (Codex / OpenCode)
         |                       |                            |
         | 1. Request Task       |                            |
         +---------------------->|                            |
         |                       | 2. Post Plan + Plan Hash   |
         |<----------------------+                            |
         |                                                    |
         | 3. "approve W-014 eb4d3b"                          |
         +--------------------------------------------------->|
                                 |
                                 v
        [WARRANT CLERK: Deterministic Python Gatekeeper]
        - Validates Approver Identity
        - Verifies Plan Hash Matching
        - Deterministic Git Diff Scope Check (Touched ⊆ Planned)
        - Links Hash Chain (prev_hash -> record_hash)
        - Sets GitHub Commit Status Check
```

**Why Switch is Central**: Without a shared Switch room, there is no shared evidence, no multi-agent collaboration, and no warrant.

---

## 3. The Multi-Agent Collaboration in a Switch Room

In our architecture, humans and multiple AI agents collaborate in a dedicated Switch room (`warrant-room`):

* **Human Lead (Priya)**: Defines business requirements and holds the authorization keys.
* **Builder Agent (Claude Code)**: Receives the prompt, generates an explicit plan listing every file it will touch, computes a SHA-256 plan hash, and waits for human approval before writing a single line of code.
* **Auditor Agent (Codex)**: An independent agent provider (for defense-in-depth) that reviews the resulting diff and runs test suites.
* **Warrant Clerk (Deterministic Python Agent)**: Connects to Switch via the official HTTP + SSE Agent Protocol. Clerk is **not an LLM**—it is a deterministic state machine that enforces rules mathematically.

Here is the exact transcript from the Switch room:

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
Claude Code: built W-014 branch=fix/invoice-tax-exempt commit=8f4a12c4...

[CLERK]
Clerk: Deterministic Scope Check Passed: 2 touched files strictly authorized in approved plan. GitHub commit status: PENDING.

[AUDITOR - Codex]
Codex: audit W-014 pass. Unit tests pass (18/18). Math verified. Zero regressions.

[PRIYA]
Priya: merge W-014

[CLERK]
Clerk: Warrant W-014 VERIFIED. Record hash linked: 838765aa... GitHub commit status set to SUCCESS.
```

---

## 4. Catching Agent Drift (The Out-of-Scope Demo)

What happens when an agent hallucinates or maliciously tries to touch files outside its approved scope?

In Warrant **W-015**, an agent was approved only to format currency in `src/invoice/formatter.py`. But when it generated its git patch, it secretly modified our sensitive payments module: `src/payments/stripe_gateway.py`!

Because Clerk doesn't rely on LLM prompts to decide boundaries, it executed pure mathematical set comparison:

$$\text{TouchedFiles} \subseteq \text{PlannedFiles}$$

```text
Planned: {'src/invoice/formatter.py'}
Touched: {'src/invoice/formatter.py', 'src/payments/stripe_gateway.py'}
Difference: {'src/payments/stripe_gateway.py'} -> SCOPE VIOLATION!
```

Instantly:
1. Warrant status shifted to `OUT_OF_SCOPE`.
2. A red **OUT OF SCOPE** rubber stamp was branded onto the warrant document.
3. The GitHub commit status check was flipped to `failure`, blocking any pull request merge!

---

## 5. Skeuomorphic Paper Aesthetic: A Ledger, Not a Dashboard

Modern enterprise software looks like generic blue dashboards. For Warrant, we wanted it to look and feel like an official government bond or legal ledger.

- **Tokens**: Warm paper background (`#F6F1E7`), deep ink (`#1A1A1A`), hairline rules (`#D9D0BE`).
- **Typography**: Newsreader serif for display titles, Inter for UI, and JetBrains Mono for cryptographic hashes.
- **The Skeuomorphic Stamp**: The `WarrantCard` component features subtle paper grain, a double-rule border, and perforated edges. When approved, an oxblood **APPROVED** stamp physically presses onto the page with a rotate-and-settle CSS keyframe animation.
- **Keyboard Navigation**: Full terminal-style navigation with `j`/`k` to traverse the ledger, `Enter` to open, and `Esc` to return.

---

## 6. Standalone Offline Verification CLI

A ledger is useless if you have to trust the web UI. Anyone on the security team can clone the repo and run the standalone verification tool directly against git commits:

```bash
$ python warrant.py verify 8f4a12c4b1239840294104928172635418294021

============================================================
 WARRANT VERIFICATION PROTOCOL v1.0
 Target Commit: 8f4a12c4b1239840294104928172635418294021
============================================================
[*] Found Warrant: W-014 | Approver: priya | Status: APPROVED_MERGE
[1/4] Checking Plan Hash... -> MATCH
[2/4] Checking Diff Hash... -> MATCH
[3/4] Deterministic Scope Check... -> CLEAN (2/2 files authorized)
[4/4] Verifying Hash Chain Link... -> LINKED (838765aa... -> prev)

>>> [RESULT] VERIFIED <<<
Evidence traced to human authorization in Switch Room.
```

And if a single byte in the SQLite database is altered:

```bash
$ python warrant.py verify 8f4a12c4b... --tamper

[SIMULATION] Injecting byte tamper into record payload...
[4/4] Verifying Hash Chain Link... -> FAILED
[RESULT] UNAUTHORIZED: Hash chain integrity check FAILED. Record tampered.
```

---

## 7. What We Loved About Switch & What We Would Improve

Participating in the **Flip the Switch Hackathon** gave us deep hands-on experience with Switch's core architecture. Here is our honest feedback:

### What We Loved:
1. **Multi-Agent Reality**: Bringing Claude Code, Codex, and humans into one room turns isolated coding sessions into collaborative team engineering.
2. **Standardized Agent Protocol**: The HTTP + SSE wire protocol was effortless to connect with our Python service.
3. **Local-First with Bundled Mattermost**: Being able to test multi-agent rooms locally without setting up third-party cloud chat bots saved hours of debugging.

### What We Would Improve:
1. **Cryptographically Signed Sender Attestation**: Chat bridges normalize sender tags differently. Having a cryptographically signed identity header in event payloads would enable true zero-trust compliance against display name spoofing.
2. **Cross-Bridge UI Primitives**: A standardized component abstraction for buttons and modals that automatically falls back to typed chat commands on CLI/terminal bridges would elevate human-in-the-loop UX.

---

## Conclusion

As coding agents become standard teammates, software teams need accountability. **Warrant** proves that with Switch's shared multi-agent rooms and deterministic math, we can unleash autonomous agents while keeping human leads firmly in control.

Check out our live deployment and code on GitHub:
- 🌐 **Live Web App**: [warrant-web-ncno.onrender.com](https://warrant-web-ncno.onrender.com)
- 📦 **GitHub**: [Shreyansh00987/Warrant](https://github.com/Shreyansh00987/Warrant)
