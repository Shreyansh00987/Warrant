# Blocker & Edge Case Log (docs/BLOCKERS.md)

This log documents every architectural boundary, platform constraint, and edge-case resolution encountered during the development of Warrant.

---

## 1. Chat Bridge Sender Identity vs. Spoofing
* **Issue**: Different Switch chat bridges (Slack vs. Mattermost vs. Discord) format message author identifiers differently (e.g., `sender_id`, `author`, `username`, `user_id`). Furthermore, on self-hosted local chat instances without SSO enforcement, display names could theoretically be spoofed.
* **Resolution**:
  1. Clerk normalizes incoming author tags across `sender`, `author`, `user_id`, and `sender_id`.
  2. Clerk matches the actor against `APPROVER_ALLOWLIST`.
  3. Clerk supports an optional secondary secret passphrase (`APPROVER_PASSPHRASE`) in the typed command: `approve W-014 a3f9c2 [passphrase]`.
  4. If sender identity cannot be verified, Clerk **fails closed** (`status = pending`).

---

## 2. Unavailability of "Switch Trust" Guardrails
* **Issue**: The hackathon brief noted that Switch Trust guardrail APIs are not available for direct reliance in this competition.
* **Resolution**:
  Warrant never relies on prompt-based or platform-side guardrails. Instead, **Warrant Clerk** implements a deterministic, mathematical Python set comparison:
  $$\text{TouchedFiles} \subseteq \text{PlannedFiles}$$
  If an agent touches any file not in the approved plan, it is blocked deterministically.

---

## 3. Absence of Interactive Buttons in Multi-Platform Bridges
* **Issue**: Not all chat bridges supported by Switch (e.g. basic terminal clients or certain IRC/Telegram bridges) support interactive Slack-style blocks or buttons.
* **Resolution**:
  Warrant strictly uses **typed chat commands**:
  - `approve W-XXX <plan-hash>`
  - `built W-XXX branch=<branch> commit=<sha> diff=<diff>`
  - `audit W-XXX <pass|block> <notes>`
  - `merge W-XXX`
  No interactive buttons or modals are claimed or required in the chat interface.

---

## 4. Hash Announcing Invariance
* **Issue**: When a coding agent prints a plan and includes its own hash at the bottom (`Plan hash: a688e9...`), hashing the entire message naively leads to a circular dependency.
* **Resolution**:
  `clerk/hasher.py` excludes trailing self-referential hash announcement lines from normalization before calculating SHA-256. This guarantees that plan hashes are deterministic and stable.
