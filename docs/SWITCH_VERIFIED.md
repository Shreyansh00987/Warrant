# Switch Capability Verification (docs/SWITCH_VERIFIED.md)

This document records the exact Switch platform capabilities verified from official sources, alongside unverified assumptions and their concrete fallbacks, as required by the Warrant design specification.

---

## 1. Verified Capabilities

The following capabilities have been confirmed via the official repositories and documentation:
- **Repository**: [https://github.com/sandbox-quantum/switch](https://github.com/sandbox-quantum/switch)
- **Documentation**: [https://docs.switchagents.ai/switch-rooms/getting-started](https://docs.switchagents.ai/switch-rooms/getting-started)
- **Hackathon Official Site & Rules**: [https://wemakedevs.org/hackathons/switch](https://wemakedevs.org/hackathons/switch) and [https://wemakedevs.org/hackathons/switch/rules](https://wemakedevs.org/hackathons/switch/rules)

| Capability | Official Reference | Notes / Verified Details |
|---|---|---|
| **Multi-Agent Shared Rooms** | `docs.switchagents.ai/switch-rooms/getting-started`<br>`github.com/sandbox-quantum/switch` | Switch bridges human chat platforms (Slack, Discord, MS Teams, Telegram, Mattermost) into shared collaborative "rooms" where humans and AI agents interact. |
| **Agent Template Schema (YAML)** | `examples/agent-templates/triage-pair.template.yaml`<br>`github.com/sandbox-quantum/switch` | Agent templates define:<br>• `agents`: `name`, `description`, `addressing` (`anyone`, `owner-agents`), `provider` (`claude`, `codex`, `opencode`), `location`, `directory`, `instructions`.<br>• `room`: `name`, `description`, `bridge`, `agents`, `users`, `kickoff`. |
| **Agent Protocol (HTTP + SSE / WS)** | `core/switch_core/bridges/agent/protocol/`<br>`docs.switchagents.ai` | Switch provides an Agent Protocol wire protocol for agent connection, presence, and event delivery. Outbound requests use HTTP; real-time event streams use Server-Sent Events (SSE) or WebSockets. |
| **Coding Agent Runtimes** | Switch Console quickstart docs | Claude Code, Codex, and OpenCode work through the Switch Console desktop companion application. |
| **Local Bundled Chat Bridge** | `github.com/sandbox-quantum/switch` README | For local self-hosted setups, Switch bundles Mattermost to provide local room and channel infrastructure without third-party cloud chat dependencies. |
| **Guardrails ("Switch Trust") Status** | Official Hackathon FAQ & Guidelines | Switch Trust guardrails are not required or assumed to be operational for this hackathon track. Warrant implements its own deterministic enforcement layer (Clerk). |

---

## 2. Unverified / Assumed Capabilities & Fallbacks

To ensure absolute engineering honesty and zero hallucinated features, all unverified items and their fallback behaviors are documented below:

### A. Sender Identity Field in Event Frames
* **Assumption**: The incoming event frame delivered to agents via SSE or webhook contains an authenticated identifier for the message author (e.g., `sender_id`, `author`, `user_id`, or `username`).
* **Unverified Aspect**: Because bridge drivers (Slack vs Mattermost vs Discord) normalize user fields differently, the exact key name and authenticity level may vary by bridge.
* **Fallback**:
  1. Clerk inspects `sender_id`, `author`, `user_id`, or `username` from the event payload against `APPROVER_ALLOWLIST`.
  2. If the bridge does not provide an immutable user ID or runs in an untrusted environment, Clerk supports an optional `APPROVER_PASSPHRASE` appended to the typed command (`approve W-014 <plan-hash> <passphrase>`).
  3. If identity cannot be validated by either method, Clerk **fails closed** (status remains `pending` with an explicit reason logged).

### B. Outbound Chat Message Dispatch Endpoint
* **Assumption**: Agents post replies back into the room via `POST /gateway/rooms/{room_id}/messages` or the bridge HTTP API.
* **Unverified Aspect**: The exact URL path for posting chat messages varies depending on whether connecting to `switch-core` directly or through the Mattermost driver.
* **Fallback**:
  1. Clerk implements a modular adapter client (`SwitchClient`) that supports configurable endpoints via `SWITCH_SERVER_URL`.
  2. Clerk also exposes `POST /internal/events` to ingest room events via standard webhook/callback.
  3. A standalone replay runner (`replay_events.py`) is provided with captured fixtures so the entire lifecycle can run deterministically even if Switch is offline.

### C. Chat Platform Interactive UI Elements (Buttons / Modals)
* **Unverified / Unsupported**: Switch does not guarantee that interactive message buttons (Slack blocks, Discord components) render uniformly across all bridges.
* **Fallback**: Warrant strictly uses **typed chat commands** (`approve W-014 <plan-hash>`, `merge W-014`). No interactive buttons or modals are claimed or required in the chat interface.

### D. Cryptographic Ledger Claims
* **Reality**: The ledger is a **hash-linked ledger** (`prev_hash`, `record_hash` using SHA-256), binding request text, plan hash, diff hash, scope check result, and approver metadata.
* **Honesty Statement**: It is not a zero-knowledge or trustless Byzantine-fault-tolerant blockchain; a compromised Clerk server could forge records. It provides verifiable audit trails under standard server trust assumptions. Optional ed25519 signing can be added as a stretch goal.
