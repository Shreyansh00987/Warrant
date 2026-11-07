"""
Warrant Clerk Comprehensive Test Suite.
Validates:
- Plan hash normalization and prefix matching
- Deterministic scope check (clean vs drift)
- Allowlist authorization and fail-closed security
- Passphrase verification
- State machine transitions & two gates
- Hash chain integrity & tamper detection
- API functions and seed retrieval
"""

import os
import pytest

from clerk.db import get_warrant, init_db, list_warrants
from clerk.hasher import (
    GENESIS_HASH,
    compute_diff_hash,
    compute_plan_hash,
    compute_record_hash,
    matches_plan_hash,
    normalize_text,
)
from clerk.main import app, get_stats, get_warrants, health, verify_commit
from clerk.parser import parse_chat_message
from clerk.scope import check_scope, parse_diff_files, parse_planned_files
from clerk.seed import seed_database
from clerk.service import is_approver_authorized, process_room_event

TEST_DB = "test_warrant.db"


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{TEST_DB}")
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass
    init_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass


def test_text_normalization_and_plan_hash():
    text_crlf = "### Plan\r\n- file1.py  \r\n- file2.py\r\n"
    text_lf = "### Plan\n- file1.py\n- file2.py"
    norm_crlf = normalize_text(text_crlf)
    norm_lf = normalize_text(text_lf)
    assert norm_crlf == norm_lf

    h1 = compute_plan_hash(text_crlf)
    h2 = compute_plan_hash(text_lf)
    assert h1 == h2
    assert len(h1) == 64
    assert matches_plan_hash(h1, h1[:6])
    assert matches_plan_hash(h1, h1[:8].upper())  # case insensitive
    assert not matches_plan_hash(h1, "ffffffff")


def test_deterministic_scope_check():
    plan_md = """
    Target files:
    - src/invoice/calculator.py
    - tests/test_calculator.py
    """
    planned = parse_planned_files(plan_md)
    assert "src/invoice/calculator.py" in planned
    assert "tests/test_calculator.py" in planned

    # Clean diff
    clean_diff = """
    diff --git a/src/invoice/calculator.py b/src/invoice/calculator.py
    --- a/src/invoice/calculator.py
    +++ b/src/invoice/calculator.py
    """
    clean_touched = parse_diff_files(clean_diff)
    res_clean = check_scope(planned, clean_touched)
    assert res_clean.is_clean is True
    assert res_clean.scope_result == "CLEAN"
    assert len(res_clean.offending_files) == 0

    # Drift diff touching payments
    drift_diff = """
    diff --git a/src/invoice/calculator.py b/src/invoice/calculator.py
    --- a/src/invoice/calculator.py
    +++ b/src/invoice/calculator.py
    diff --git a/src/payments/gateway.py b/src/payments/gateway.py
    --- a/src/payments/gateway.py
    +++ b/src/payments/gateway.py
    """
    drift_touched = parse_diff_files(drift_diff)
    res_drift = check_scope(planned, drift_touched)
    assert res_drift.is_clean is False
    assert res_drift.scope_result == "SCOPE_VIOLATION"
    assert "src/payments/gateway.py" in res_drift.offending_files


def test_approver_allowlist_and_fail_closed(monkeypatch):
    monkeypatch.setenv("APPROVER_ALLOWLIST", "priya,alec,security-lead")
    monkeypatch.delenv("APPROVER_PASSPHRASE", raising=False)

    auth, reason = is_approver_authorized("priya")
    assert auth is True

    auth, reason = is_approver_authorized("@alec")
    assert auth is True

    # Untrusted user must fail closed
    auth, reason = is_approver_authorized("mallory")
    assert auth is False
    assert "not in the approver allowlist" in reason


def test_approver_passphrase_hardening(monkeypatch):
    monkeypatch.setenv("APPROVER_ALLOWLIST", "priya")
    monkeypatch.setenv("APPROVER_PASSPHRASE", "top-secret-warrant")

    # Correct actor, missing passphrase -> fails
    auth, reason = is_approver_authorized("priya", None)
    assert auth is False
    assert "passphrase" in reason.lower()

    # Correct actor, wrong passphrase -> fails
    auth, reason = is_approver_authorized("priya", "wrong-passphrase")
    assert auth is False

    # Correct actor, correct passphrase -> succeeds
    auth, reason = is_approver_authorized("priya", "top-secret-warrant")
    assert auth is True


def test_full_clean_workflow_lifecycle():
    # 1. Request
    res1 = process_room_event(
        {
            "id": "msg-1",
            "sender": "priya",
            "content": "Priya: @claude-code fix invoice bug (W-100)",
        },
        db_path=TEST_DB,
    )
    assert res1["handled"] is True
    assert res1["status"] == "REQUESTED"

    # 2. Plan
    plan_text = "Plan for W-100\nTarget files:\n- src/invoice/tax.py\nPlan hash: will be computed"
    res2 = process_room_event(
        {
            "id": "msg-2",
            "sender": "claude-code",
            "content": plan_text,
        },
        db_path=TEST_DB,
    )
    assert res2["handled"] is True
    assert res2["status"] == "PLANNED"
    plan_hash = res2["plan_hash"]

    # 3. Plan Approval (bound to hash prefix)
    res3 = process_room_event(
        {
            "id": "msg-3",
            "sender": "priya",
            "content": f"approve W-100 {plan_hash[:6]}",
        },
        db_path=TEST_DB,
    )
    assert res3["handled"] is True
    assert res3["status"] == "APPROVED_PLAN"

    # 4. Build Report
    diff_text = """diff --git a/src/invoice/tax.py b/src/invoice/tax.py
--- a/src/invoice/tax.py
+++ b/src/invoice/tax.py
@@ -1 +1 @@
-tax = 0.25
+tax = 0.20
"""
    res4 = process_room_event(
        {
            "id": "msg-4",
            "sender": "claude-code",
            "content": f"built W-100 branch=fix/tax commit=112233445566 diff={diff_text}",
        },
        db_path=TEST_DB,
    )
    assert res4["handled"] is True
    assert res4["status"] == "BUILT"
    assert res4["scope_result"] == "CLEAN"

    # 5. Auditor Review
    res5 = process_room_event(
        {
            "id": "msg-5",
            "sender": "codex",
            "content": "audit W-100 pass All 12 tests pass cleanly.",
        },
        db_path=TEST_DB,
    )
    assert res5["handled"] is True
    assert res5["status"] == "AUDITED"

    # 6. Merge Approval
    res6 = process_room_event(
        {
            "id": "msg-6",
            "sender": "priya",
            "content": "merge W-100",
        },
        db_path=TEST_DB,
    )
    assert res6["handled"] is True
    assert res6["status"] == "APPROVED_MERGE"
    assert "record_hash" in res6


def test_drift_detection_blocks_and_fails_closed():
    # 1. Plan
    plan_text = "Plan for W-200\nTarget files:\n- src/invoice/tax.py"
    p_hash = compute_plan_hash(plan_text)
    process_room_event(
        {"id": "p-1", "sender": "claude-code", "content": plan_text},
        db_path=TEST_DB,
    )
    # 2. Approve
    process_room_event(
        {"id": "p-2", "sender": "priya", "content": f"approve W-200 {p_hash[:6]}"},
        db_path=TEST_DB,
    )
    # 3. Build with unauthorized payment modification
    drift_diff = """diff --git a/src/invoice/tax.py b/src/invoice/tax.py
--- a/src/invoice/tax.py
+++ b/src/invoice/tax.py
diff --git a/src/payments/keys.py b/src/payments/keys.py
--- a/src/payments/keys.py
+++ b/src/payments/keys.py
"""
    res3 = process_room_event(
        {
            "id": "p-3",
            "sender": "claude-code",
            "content": f"built W-200 branch=drift commit=deadbeef diff={drift_diff}",
        },
        db_path=TEST_DB,
    )
    assert res3["status"] == "OUT_OF_SCOPE"
    assert res3["scope_result"] == "SCOPE_VIOLATION"
    assert "src/payments/keys.py" in res3["offending_files"]

    # 4. Attempt to merge must fail closed
    res4 = process_room_event(
        {"id": "p-4", "sender": "priya", "content": "merge W-200"},
        db_path=TEST_DB,
    )
    assert res4["handled"] is False
    assert "Scope check is SCOPE_VIOLATION" in res4["error"]


def test_tamper_detection():
    seed_database(TEST_DB)
    w = get_warrant("W-014", db_path=TEST_DB)
    assert w is not None

    computed = compute_record_hash(
        prev_hash=w["prev_hash"],
        warrant_id=w["id"],
        plan_hash=w["plan_hash"],
        diff_hash=w["diff_hash"],
        scope_result=w["scope_result"],
        approved_by=w["approved_by"],
        status=w["status"],
    )
    assert w["record_hash"] == computed

    # If diff text or approver was altered in SQLite
    tampered_hash = compute_record_hash(
        prev_hash=w["prev_hash"],
        warrant_id=w["id"],
        plan_hash=w["plan_hash"],
        diff_hash="tampered_diff_hash",
        scope_result=w["scope_result"],
        approved_by=w["approved_by"],
        status=w["status"],
    )
    assert w["record_hash"] != tampered_hash


def test_api_endpoints():
    seed_database(TEST_DB)
    # Health
    assert health()["status"] == "healthy"

    # Warrants
    warrants = get_warrants()
    assert len(warrants) >= 2

    # Stats
    stats = get_stats()
    assert stats["approved"] >= 1
    assert stats["out_of_scope"] >= 1

    # Verify W-014 commit
    v = verify_commit("8f4a12c4b1239840294104928172635418294021")
    assert v["verified"] is True
    assert v["status"] == "VERIFIED"

    # Verify W-015 drift commit
    v = verify_commit("e39a58b291049102948201948201948201948201")
    assert v["verified"] is False
    assert v["status"] == "UNAUTHORIZED"
    assert "SCOPE VIOLATION" in v["reason"]
