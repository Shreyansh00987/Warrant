# Warrant Implementation Plan & Task List (docs/IMPLEMENTATION_PLAN.md)

## Decisions
1. **Approver Identity Strategy**:
   - Primary: Match sender ID / author name against `APPROVER_ALLOWLIST` (e.g. `priya`, `alec`).
   - Secondary / Hardening: Support optional passphrase in typed chat command (`approve W-014 a3f9c2 [passphrase]`) via `APPROVER_PASSPHRASE`.
   - Security rule: If sender cannot be verified, fail closed (`status = pending`).
2. **Database**: SQLite default (path `warrant.db`), async SQLAlchemy or standard SQLite3 for zero-friction local setup and predictable docker mounting.
3. **API Contracts**:
   - `POST /internal/events` (Ingest Switch room event stream / webhooks)
   - `GET /api/warrants` (List all warrants, filters for status/source)
   - `GET /api/warrants/{id}` (Warrant detail, hash proof, timeline)
   - `GET /api/files/{path:path}/provenance` (File provenance & jump to chat excerpt)
   - `GET /api/verify/{sha}` (Verification proof for a commit sha)
   - `GET /api/stats` (Ledger counters: approved, blocked, out-of-scope, pending)
   - `GET /api/settings` (Runtime config, approver allowlist, GitHub status config, real vs seeded counts)
4. **UI Design System**:
   - Paper (`#F6F1E7`), ink (`#1A1A1A`), secondary text (`#5B5648`), rule (`#D9D0BE`), oxblood stamp (`#8B1E2D`), verified green (`#2F6B3B`).
   - Skeuomorphic `WarrantCard` and `Stamp` with rotating/scaling press animation and paper perforation border.
   - 5 views:
     1. Landing (`/`) with Hero Warrant & Chat-Blame comparison.
     2. Ledger (`/ledger`) dense tabular view with keyboard nav (`j`/`k`/`Enter`/`Esc`).
     3. Detail (`/w/[id]`) with skeuomorphic card, progress timeline, diff scope inspector, and hash chain proof.
     4. File Provenance (`/files/[...path]`) with file change history linked to chat authorizations.
     5. Settings (`/settings`) with approver allowlist, room mapping, and Real vs Seeded toggle/stats.

---

## Detailed Task Breakdown

### Phase 2: Clerk Core & Engine
- [ ] `clerk/db.py`: Database models (`warrants`, `events`, `records`) and schema migrations.
- [ ] `clerk/hasher.py`: Deterministic SHA-256 hashing for plans, git diffs, and hash chain linking.
- [ ] `clerk/parser.py`: Robust chat command parser for `approve W-XXX <hash> [passphrase]` and `merge W-XXX`.
- [ ] `clerk/scope.py`: Deterministic scope checker comparing planned file list vs actual git diff file list.
- [ ] `clerk/github.py`: Commit status dispatcher (updates GitHub REST API or gracefully displays unconfigured).
- [ ] `clerk/service.py`: Business logic coordinating the two gates and fail-closed state transitions.
- [ ] `clerk/main.py`: FastAPI application exposing internal event ingester and public API endpoints.
- [ ] `verify/warrant_verify.py`: Standalone CLI tool for `warrant verify <sha>` and tampered record detection.
- [ ] `clerk/seed.py`: Deterministic seeding script generating W-014 (passed invoice refactor) and W-015 (payments scope drift violation), marked `source=seeded`.
- [ ] Unit & Integration Tests: Test plan hash binding, allowlist checks, scope violation detection, hash chain tampering detection, and fail-closed defaults.

### Phase 3: Ledger UI (Next.js 15+ / React 19 / Tailwind)
- [ ] Scaffold Next.js TypeScript project in `web/`.
- [ ] Configure Tailwind theme with paper/ink tokens, typography, and skeuomorphic styles.
- [ ] Component: `WarrantCard` with paper grain, double-rule borders, and soft paper drop-shadow.
- [ ] Component: `Stamp` with oxblood "APPROVED" and "OUT OF SCOPE" press animation and reduced-motion support.
- [ ] Component: `WorkflowPath` showing Request -> Plan -> Approve -> Build -> Audit -> Merge with pulsing active stage.
- [ ] Component: `ScopeInspector` highlighting clean vs offending out-of-scope files.
- [ ] Screen 1: Landing (`/`) featuring hero warrant and inline line-by-line chat authorization blame view.
- [ ] Screen 2: Ledger (`/ledger`) with dense tabular layout, summary counters, filter tabs, and keyboard navigation.
- [ ] Screen 3: Detail (`/w/[id]`) with full card view, chat excerpts, hash verification modal, and auditor notes.
- [ ] Screen 4: File Provenance (`/files/[...path]`) showing historical authorizations for any given file.
- [ ] Screen 5: Settings (`/settings`) displaying approver allowlist, GitHub status integration health, and Real vs Seeded breakdown.

### Phase 4: Real Switch Integration & Replay Fixtures
- [ ] `switch/agent-templates/warrant-room.template.yaml`: Multi-agent room YAML following official Switch format.
- [ ] `switch/kickoff.txt` & setup scripts.
- [ ] `clerk/switch_client.py`: Protocol client connecting to Switch HTTP + SSE stream.
- [ ] Event Fixtures: Capture and bundle realistic Switch room event logs (`fixtures/pass_run.json`, `fixtures/drift_run.json`).
- [ ] `clerk/replay.py`: Standalone replay runner to replay real Switch event streams directly into Clerk.

### Phase 5: Target Demo Repo & Submission Package
- [ ] `demo-repo/`: Small service with invoice handler, tests, and a `payments/` module for drift demonstration.
- [ ] `docker-compose.yml` & Dockerfiles for Clerk + Web UI.
- [ ] `docs/REAL_VS_STAGED.md`: 100% transparent audit of real vs staged components.
- [ ] `docs/DEMO_SCRIPT.md`: Step-by-step 2:30 video recording shot list.
- [ ] `docs/BLOCKERS.md`: Documented edge cases or unverified assumptions.
- [ ] `README.md`: High-impact presentation, architecture diagram, 30-second problem statement, installation guide, transcript, and license notes.
