# Setting Up Warrant in Switch Console (switch/setup.md)

This guide walks you through connecting Warrant to your local Switch room.

---

## Prerequisites
1. **Switch Console**: Downloaded and running on your machine ([Switch Quickstart](https://docs.switchagents.ai/switch-rooms/getting-started)).
2. **AI Provider Credentials**:
   - Claude Code session active (`claude`).
   - OpenAI Codex or OpenCode CLI configured.
3. **Warrant Stack Running**:
   ```bash
   python warrant.py serve --port 8000
   ```
   and in a second terminal:
   ```bash
   cd web && npm run dev
   ```

---

## Step 1: Create the Room Template
1. In Switch Console, navigate to **Templates** → **Import Template**.
2. Select `switch/agent-templates/warrant-room.template.yaml`.
3. Set your team identifier (e.g., `acme`).
4. Select your bridge:
   - For local offline demo: select the bundled **Mattermost** bridge.
   - For team chat: select **Slack**, **Discord**, or **Teams**.

---

## Step 2: Provision the Agents
1. Attach **Claude Code** to the `builder` slot.
2. Attach **Codex** (or **OpenCode**) to the `auditor` slot.
3. Attach **Warrant Clerk** to the `clerk` slot (running at `http://localhost:8000/internal/events`).

---

## Step 3: Run the Kickoff
Send the kickoff message (found in `switch/kickoff.txt`) to the room to initialize the collaboration session.

---

## Step 4: Execute the Authorization Flow
1. **Human Request**:
   ```text
   @acme-builder fix invoice tax calculation on exempt items (W-014)
   ```
2. **Builder Emits Plan**:
   Builder posts the planned files (`src/invoice/calculator.py`, `tests/test_calculator.py`) and plan hash prefix (`a3f9c2`).
3. **Human Approval**:
   ```text
   approve W-014 a3f9c2
   ```
4. **Builder Emits Diff**:
   Builder implements on `fix/invoice-tax` and posts commit SHA and diff.
5. **Clerk Scope Check**:
   Clerk deterministically checks that all touched files are in the plan.
6. **Auditor Review**:
   Auditor posts:
   ```text
   audit W-014 pass All unit tests pass, no unauthorized files touched.
   ```
7. **Human Merge Approval**:
   ```text
   merge W-014
   ```
8. **View Ledger**:
   Open `http://localhost:3000/w/W-014` to inspect the skeuomorphic warrant card, pressed oxblood APPROVED stamp, and hash chain proof.
