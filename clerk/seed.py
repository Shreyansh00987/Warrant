"""
Warrant Realistic Seed Data Generator.
Generates:
- W-014: Realistic passed invoice tax fix (Priya approved, scope CLEAN, auditor PASS, status APPROVED_MERGE)
- W-015: Realistic drift attempt (Priya approved formatter only, touched payments/stripe_gateway.py, scope SCOPE_VIOLATION, status OUT_OF_SCOPE)
All marked source="seeded" and hash-linked.
"""

from __future__ import annotations
import os
from datetime import datetime, timezone, timedelta
from clerk.db import (
    init_db,
    record_file_provenance,
    save_event,
    save_warrant,
)
from clerk.hasher import (
    GENESIS_HASH,
    compute_diff_hash,
    compute_plan_hash,
    compute_record_hash,
)

PLAN_W014 = """### Task Specification
Fix incorrect tax calculation when invoice line items are flagged `tax_exempt=True`.

### Proposed Changes
- In `src/invoice/calculator.py`: Add an exemption check in `calculate_subtotal_and_tax()` before applying VAT rate.
- In `tests/test_calculator.py`: Add test cases `test_tax_exempt_item()` and `test_mixed_taxable_and_exempt()`.

### Target Files
- `src/invoice/calculator.py`
- `tests/test_calculator.py`
"""

DIFF_W014 = """diff --git a/src/invoice/calculator.py b/src/invoice/calculator.py
--- a/src/invoice/calculator.py
+++ b/src/invoice/calculator.py
@@ -14,6 +14,8 @@ def calculate_tax(items, tax_rate=0.20):
     total_tax = 0.0
     for item in items:
+        if item.get("tax_exempt", False):
+            continue
         total_tax += item["price"] * item["quantity"] * tax_rate
     return round(total_tax, 2)
diff --git a/tests/test_calculator.py b/tests/test_calculator.py
--- a/tests/test_calculator.py
+++ b/tests/test_calculator.py
@@ -28,3 +28,11 @@ def test_taxable_item():
+def test_tax_exempt_item():
+    items = [{"price": 100.0, "quantity": 1, "tax_exempt": True}]
+    assert calculate_tax(items) == 0.0
"""

PLAN_W015 = """### Task Specification
Format currency display on invoice summaries using ISO 4217 standard formatting.

### Proposed Changes
- In `src/invoice/formatter.py`: Enhance `format_currency()` to support multi-currency symbols and decimal grouping.

### Target Files
- `src/invoice/formatter.py`
"""

DIFF_W015 = """diff --git a/src/invoice/formatter.py b/src/invoice/formatter.py
--- a/src/invoice/formatter.py
+++ b/src/invoice/formatter.py
@@ -5,4 +5,7 @@ def format_currency(amount, currency="USD"):
+    if currency == "USD":
+        return f"${amount:,.2f}"
+    return f"{amount:,.2f} {currency}"
diff --git a/src/payments/stripe_gateway.py b/src/payments/stripe_gateway.py
--- a/src/payments/stripe_gateway.py
+++ b/src/payments/stripe_gateway.py
@@ -12,2 +12,4 @@ def charge_customer(customer_id, amount_cents, currency="usd"):
+    # DRIFT: Unplanned modification in payment gateway credentials handler
+    stripe_options = {"currency_override": currency.lower()}
"""


def seed_database(db_path: str | None = None) -> None:
    init_db(db_path)

    base_time = datetime(2026, 11, 7, 9, 0, 0, tzinfo=timezone.utc)

    # ----------------------------------------------------
    # SEED W-014: CLEAN RUN (APPROVED & MERGED)
    # ----------------------------------------------------
    t1 = (base_time).isoformat()
    t2 = (base_time + timedelta(minutes=2)).isoformat()
    t3 = (base_time + timedelta(minutes=5)).isoformat()
    t4 = (base_time + timedelta(minutes=15)).isoformat()
    t5 = (base_time + timedelta(minutes=18)).isoformat()
    t6 = (base_time + timedelta(minutes=22)).isoformat()

    plan_hash_14 = compute_plan_hash(PLAN_W014)
    diff_hash_14 = compute_diff_hash(DIFF_W014)

    record_hash_14 = compute_record_hash(
        prev_hash=GENESIS_HASH,
        warrant_id="W-014",
        plan_hash=plan_hash_14,
        diff_hash=diff_hash_14,
        scope_result="CLEAN",
        approved_by="priya",
        status="APPROVED_MERGE",
    )

    warrant_14 = {
        "id": "W-014",
        "room_id": "warrant-room",
        "request_msg_id": "msg-014-req",
        "requester": "priya",
        "plan_md": PLAN_W014,
        "plan_hash": plan_hash_14,
        "approved_by": "priya",
        "approved_msg_id": "msg-014-appr",
        "approved_at": t3,
        "branch": "fix/invoice-tax-exempt",
        "commit_sha": "8f4a12c4b1239840294104928172635418294021",
        "diff_text": DIFF_W014,
        "diff_hash": diff_hash_14,
        "scope_result": "CLEAN",
        "offending_files": [],
        "auditor_verdict": "PASS",
        "auditor_notes": "Unit tests pass (18/18). Exemption logic conforms to tax spec. No unauthorized files touched.",
        "status": "APPROVED_MERGE",
        "source": "seeded",
        "prev_hash": GENESIS_HASH,
        "record_hash": record_hash_14,
        "created_at": t1,
        "updated_at": t6,
    }
    save_warrant(warrant_14, db_path=db_path)

    # Events for W-014
    save_event(
        "evt-014-1", "W-014", "request", "priya", "msg-014-req",
        "Priya: @claude-code fix invoice tax calculation for non-taxable items. See issue #104. (W-014)",
        {"issue": 104}, t1, db_path,
    )
    save_event(
        "evt-014-2", "W-014", "plan", "claude-code", "msg-014-plan",
        f"Claude Code: Plan for W-014. Target files: src/invoice/calculator.py, tests/test_calculator.py. Plan hash: {plan_hash_14[:8]}",
        {"plan_hash": plan_hash_14}, t2, db_path,
    )
    save_event(
        "evt-014-3", "W-014", "approval", "priya", "msg-014-appr",
        f"Priya: approve W-014 {plan_hash_14[:6]}",
        {"plan_hash_prefix": plan_hash_14[:6]}, t3, db_path,
    )
    save_event(
        "evt-014-4", "W-014", "build", "claude-code", "msg-014-build",
        "Claude Code: built W-014 branch=fix/invoice-tax-exempt commit=8f4a12c4b1239840294104928172635418294021",
        {"branch": "fix/invoice-tax-exempt", "commit_sha": "8f4a12c4b1239840294104928172635418294021"}, t4, db_path,
    )
    save_event(
        "evt-014-5", "W-014", "audit", "codex", "msg-014-audit",
        "Codex: audit W-014 pass Unit tests pass (18/18). Math verified. Zero regressions.",
        {"verdict": "PASS"}, t5, db_path,
    )
    save_event(
        "evt-014-6", "W-014", "merge", "priya", "msg-014-merge",
        "Priya: merge W-014",
        {"merged_by": "priya"}, t6, db_path,
    )

    # File provenance records
    record_file_provenance(
        "src/invoice/calculator.py", "W-014", "8f4a12c4b1239840294104928172635418294021",
        "APPROVED_MERGE", "priya", "Authorized tax calculation fix by Priya in W-014", db_path,
    )
    record_file_provenance(
        "tests/test_calculator.py", "W-014", "8f4a12c4b1239840294104928172635418294021",
        "APPROVED_MERGE", "priya", "Authorized unit test addition by Priya in W-014", db_path,
    )

    # ----------------------------------------------------
    # SEED W-015: DRIFT RUN (SCOPE VIOLATION & BLOCKED)
    # ----------------------------------------------------
    d1 = (base_time + timedelta(hours=1)).isoformat()
    d2 = (base_time + timedelta(hours=1, minutes=2)).isoformat()
    d3 = (base_time + timedelta(hours=1, minutes=4)).isoformat()
    d4 = (base_time + timedelta(hours=1, minutes=12)).isoformat()
    d5 = (base_time + timedelta(hours=1, minutes=15)).isoformat()

    plan_hash_15 = compute_plan_hash(PLAN_W015)
    diff_hash_15 = compute_diff_hash(DIFF_W015)

    record_hash_15 = compute_record_hash(
        prev_hash=record_hash_14,
        warrant_id="W-015",
        plan_hash=plan_hash_15,
        diff_hash=diff_hash_15,
        scope_result="SCOPE_VIOLATION",
        approved_by="priya",
        status="OUT_OF_SCOPE",
    )

    warrant_15 = {
        "id": "W-015",
        "room_id": "warrant-room",
        "request_msg_id": "msg-015-req",
        "requester": "alec",
        "plan_md": PLAN_W015,
        "plan_hash": plan_hash_15,
        "approved_by": "priya",
        "approved_msg_id": "msg-015-appr",
        "approved_at": d3,
        "branch": "feat/iso-currency",
        "commit_sha": "e39a58b291049102948201948201948201948201",
        "diff_text": DIFF_W015,
        "diff_hash": diff_hash_15,
        "scope_result": "SCOPE_VIOLATION",
        "offending_files": ["src/payments/stripe_gateway.py"],
        "auditor_verdict": "BLOCK",
        "auditor_notes": "SCOPE VIOLATION: Agent modified src/payments/stripe_gateway.py without plan authorization. Blocked.",
        "status": "OUT_OF_SCOPE",
        "source": "seeded",
        "prev_hash": record_hash_14,
        "record_hash": record_hash_15,
        "created_at": d1,
        "updated_at": d5,
    }
    save_warrant(warrant_15, db_path=db_path)

    # Events for W-015
    save_event(
        "evt-015-1", "W-015", "request", "alec", "msg-015-req",
        "Alec: @claude-code format invoice currency to ISO 4217 standard. (W-015)",
        {"requester": "alec"}, d1, db_path,
    )
    save_event(
        "evt-015-2", "W-015", "plan", "claude-code", "msg-015-plan",
        f"Claude Code: Plan for W-015. Target files: src/invoice/formatter.py. Plan hash: {plan_hash_15[:8]}",
        {"plan_hash": plan_hash_15}, d2, db_path,
    )
    save_event(
        "evt-015-3", "W-015", "approval", "priya", "msg-015-appr",
        f"Priya: approve W-015 {plan_hash_15[:6]}",
        {"plan_hash_prefix": plan_hash_15[:6]}, d3, db_path,
    )
    save_event(
        "evt-015-4", "W-015", "build", "claude-code", "msg-015-build",
        "Claude Code: built W-015 branch=feat/iso-currency commit=e39a58b291049102948201948201948201948201",
        {"branch": "feat/iso-currency", "commit_sha": "e39a58b291049102948201948201948201948201"}, d4, db_path,
    )
    save_event(
        "evt-015-5", "W-015", "scope_check", "clerk", "msg-015-scope",
        "Clerk: SCOPE VIOLATION detected! Agent modified unapproved file 'src/payments/stripe_gateway.py'. GitHub commit status set to FAILURE.",
        {"offending_files": ["src/payments/stripe_gateway.py"]}, d4, db_path,
    )
    save_event(
        "evt-015-6", "W-015", "audit", "codex", "msg-015-audit",
        "Codex: audit W-015 block SCOPE VIOLATION: Agent modified src/payments/stripe_gateway.py without plan authorization.",
        {"verdict": "BLOCK"}, d5, db_path,
    )


if __name__ == "__main__":
    seed_database()
    print("Successfully seeded W-014 (pass) and W-015 (drift/scope violation).")
