"""
Warrant Clerk Service Layer.
The deterministic core orchestrating state transitions, plan binding, scope checks,
hash chain linking, and fail-closed security.
"""

from __future__ import annotations
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from clerk.db import (
    get_file_provenance,
    get_last_warrant,
    get_warrant,
    list_warrants,
    record_file_provenance,
    save_event,
    save_warrant,
)
from clerk.github import set_commit_status
from clerk.hasher import (
    GENESIS_HASH,
    compute_diff_hash,
    compute_plan_hash,
    compute_record_hash,
    matches_plan_hash,
)
from clerk.parser import ParsedCommand, parse_chat_message
from clerk.scope import check_scope, parse_diff_files, parse_planned_files


def get_allowlist() -> List[str]:
    raw = os.getenv("APPROVER_ALLOWLIST", "priya,alec,security-lead")
    return [name.strip().lower() for name in raw.split(",") if name.strip()]


def is_approver_authorized(actor: str, passphrase: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validates whether an actor is authorized to approve plans or merges.
    1. Actor must be in APPROVER_ALLOWLIST.
    2. If APPROVER_PASSPHRASE is configured in env, command passphrase must match.
    Fail-closed: Returns (False, reason) on any mismatch.
    """
    clean_actor = actor.strip().lower().lstrip("@")
    allowlist = get_allowlist()

    if clean_actor not in allowlist:
        return False, f"Actor '{actor}' is not in the approver allowlist ({', '.join(allowlist)})."

    required_passphrase = os.getenv("APPROVER_PASSPHRASE", "").strip()
    if required_passphrase:
        if not passphrase or passphrase.strip() != required_passphrase:
            return False, "Invalid or missing approver passphrase."

    return True, "Authorized"


def process_room_event(
    event_payload: Dict[str, Any],
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    msg_id = str(event_payload.get("id") or f"evt-{int(datetime.now(timezone.utc).timestamp()*1000)}")
    room_id = event_payload.get("room_id", "warrant-room")
    actor = (
        event_payload.get("sender")
        or event_payload.get("author")
        or event_payload.get("user_id")
        or event_payload.get("sender_id")
        or "unknown"
    )
    content = event_payload.get("content") or event_payload.get("text") or ""
    timestamp = event_payload.get("timestamp") or datetime.now(timezone.utc).isoformat()

    cmd: ParsedCommand = parse_chat_message(content)
    result: Dict[str, Any] = {"handled": False, "command_kind": cmd.kind, "actor": actor}

    # If message mentions or targets a warrant
    warrant_id = cmd.warrant_id
    if not warrant_id and cmd.kind == "unknown":
        import re
        w_match = re.search(r"\b(W-[0-9a-zA-Z_\-]+)\b", content)
        if w_match:
            warrant_id = w_match.group(1).upper()

    if not warrant_id:
        return {"handled": False, "reason": "No warrant ID detected in message"}

    # Fetch existing warrant or initialize
    warrant = get_warrant(warrant_id, db_path=db_path)
    now_iso = datetime.now(timezone.utc).isoformat()

    if not warrant:
        last_w = get_last_warrant(db_path=db_path)
        prev_hash = last_w["record_hash"] if last_w and last_w.get("record_hash") else GENESIS_HASH

        warrant = {
            "id": warrant_id,
            "room_id": room_id,
            "request_msg_id": msg_id if cmd.kind == "request" else None,
            "requester": actor if cmd.kind == "request" else "unknown",
            "plan_md": None,
            "plan_hash": None,
            "approved_by": None,
            "approved_msg_id": None,
            "approved_at": None,
            "branch": None,
            "commit_sha": None,
            "diff_text": None,
            "diff_hash": None,
            "scope_result": "PENDING",
            "offending_files": [],
            "auditor_verdict": "PENDING",
            "auditor_notes": None,
            "status": "REQUESTED",
            "source": event_payload.get("source", "live"),
            "prev_hash": prev_hash,
            "record_hash": "",
            "created_at": timestamp,
            "updated_at": now_iso,
        }

    # 1. HANDLE REQUEST
    if cmd.kind == "request":
        warrant["request_msg_id"] = msg_id
        warrant["requester"] = actor
        warrant["status"] = "REQUESTED"
        warrant["updated_at"] = now_iso
        save_warrant(warrant, db_path=db_path)
        save_event(
            event_id=f"evt-{msg_id}-req",
            warrant_id=warrant_id,
            kind="request",
            actor=actor,
            msg_id=msg_id,
            excerpt=content,
            payload=event_payload,
            at=timestamp,
            db_path=db_path,
        )
        result["handled"] = True
        result["status"] = "REQUESTED"

    # 2. HANDLE PLAN
    elif cmd.kind == "plan":
        plan_hash = compute_plan_hash(content)
        warrant["plan_md"] = content
        warrant["plan_hash"] = plan_hash
        warrant["status"] = "PLANNED"
        warrant["updated_at"] = now_iso
        save_warrant(warrant, db_path=db_path)
        save_event(
            event_id=f"evt-{msg_id}-plan",
            warrant_id=warrant_id,
            kind="plan",
            actor=actor,
            msg_id=msg_id,
            excerpt=f"Plan posted for {warrant_id} with hash {plan_hash[:8]}",
            payload={"plan_hash": plan_hash, "full_text": content},
            at=timestamp,
            db_path=db_path,
        )
        result["handled"] = True
        result["status"] = "PLANNED"
        result["plan_hash"] = plan_hash

    # 3. HANDLE APPROVAL
    elif cmd.kind == "approve":
        # Validate approver identity
        authorized, reason = is_approver_authorized(actor, cmd.passphrase)
        if not authorized:
            save_event(
                event_id=f"evt-{msg_id}-unauth",
                warrant_id=warrant_id,
                kind="unauthorized_approval",
                actor=actor,
                msg_id=msg_id,
                excerpt=f"REJECTED: Unauthorized approval attempt by '{actor}': {reason}",
                payload={"error": reason},
                at=timestamp,
                db_path=db_path,
            )
            result["handled"] = False
            result["error"] = reason
            return result

        # Validate plan hash binding
        current_plan_hash = warrant.get("plan_hash")
        if not current_plan_hash:
            result["handled"] = False
            result["error"] = f"No plan has been submitted yet for {warrant_id}."
            return result

        if not matches_plan_hash(current_plan_hash, cmd.plan_hash or ""):
            error_msg = (
                f"PLAN HASH MISMATCH: Approved hash '{cmd.plan_hash}' does not match "
                f"current plan hash '{current_plan_hash[:8]}'. Plan may have changed!"
            )
            save_event(
                event_id=f"evt-{msg_id}-mismatch",
                warrant_id=warrant_id,
                kind="hash_mismatch",
                actor=actor,
                msg_id=msg_id,
                excerpt=error_msg,
                payload={"approved_hash": cmd.plan_hash, "actual_hash": current_plan_hash},
                at=timestamp,
                db_path=db_path,
            )
            result["handled"] = False
            result["error"] = error_msg
            return result

        # Approval validated!
        warrant["approved_by"] = actor
        warrant["approved_msg_id"] = msg_id
        warrant["approved_at"] = timestamp
        warrant["status"] = "APPROVED_PLAN"
        warrant["updated_at"] = now_iso

        # Update record hash
        warrant["record_hash"] = compute_record_hash(
            prev_hash=warrant["prev_hash"],
            warrant_id=warrant_id,
            plan_hash=warrant["plan_hash"],
            diff_hash=warrant.get("diff_hash"),
            scope_result=warrant.get("scope_result", "PENDING"),
            approved_by=actor,
            status=warrant["status"],
        )
        save_warrant(warrant, db_path=db_path)

        save_event(
            event_id=f"evt-{msg_id}-appr",
            warrant_id=warrant_id,
            kind="approval",
            actor=actor,
            msg_id=msg_id,
            excerpt=f"Plan {warrant['plan_hash'][:8]} approved by {actor}",
            payload={"approved_by": actor, "plan_hash": current_plan_hash},
            at=timestamp,
            db_path=db_path,
        )
        result["handled"] = True
        result["status"] = "APPROVED_PLAN"

    # 4. HANDLE BUILD REPORT
    elif cmd.kind == "build":
        branch = cmd.branch or warrant.get("branch") or "main"
        commit_sha = cmd.commit_sha or warrant.get("commit_sha") or "unknown"
        diff_text = cmd.diff_text or warrant.get("diff_text") or ""

        # Compute diff hash
        diff_hash = compute_diff_hash(diff_text)
        warrant["branch"] = branch
        warrant["commit_sha"] = commit_sha
        warrant["diff_text"] = diff_text
        warrant["diff_hash"] = diff_hash

        # DETERMINISTIC SCOPE CHECK
        planned_files = parse_planned_files(warrant.get("plan_md") or "")
        touched_files = parse_diff_files(diff_text)
        scope_res = check_scope(planned_files, touched_files)

        warrant["scope_result"] = scope_res.scope_result
        warrant["offending_files"] = scope_res.offending_files

        if not scope_res.is_clean:
            warrant["status"] = "OUT_OF_SCOPE"
            # Set GitHub status to failure
            set_commit_status(
                commit_sha=commit_sha,
                state="failure",
                description=f"SCOPE VIOLATION: touched {', '.join(scope_res.offending_files)}",
                target_url=f"http://localhost:3000/w/{warrant_id}",
            )
        else:
            warrant["status"] = "BUILT"
            # Set GitHub status to pending audit
            set_commit_status(
                commit_sha=commit_sha,
                state="pending",
                description="Scope CLEAN. Awaiting independent auditor review.",
                target_url=f"http://localhost:3000/w/{warrant_id}",
            )

        warrant["updated_at"] = now_iso
        warrant["record_hash"] = compute_record_hash(
            prev_hash=warrant["prev_hash"],
            warrant_id=warrant_id,
            plan_hash=warrant.get("plan_hash"),
            diff_hash=diff_hash,
            scope_result=warrant["scope_result"],
            approved_by=warrant.get("approved_by"),
            status=warrant["status"],
        )
        save_warrant(warrant, db_path=db_path)

        save_event(
            event_id=f"evt-{msg_id}-build",
            warrant_id=warrant_id,
            kind="build",
            actor=actor,
            msg_id=msg_id,
            excerpt=f"Build completed on {branch} ({commit_sha[:7]}). Scope result: {scope_res.scope_result}",
            payload={
                "branch": branch,
                "commit_sha": commit_sha,
                "diff_hash": diff_hash,
                "scope_result": scope_res.scope_result,
                "offending_files": scope_res.offending_files,
                "planned_files": scope_res.planned_files,
                "touched_files": scope_res.touched_files,
            },
            at=timestamp,
            db_path=db_path,
        )
        result["handled"] = True
        result["status"] = warrant["status"]
        result["scope_result"] = scope_res.scope_result
        result["offending_files"] = scope_res.offending_files

    # 5. HANDLE AUDITOR VERDICT
    elif cmd.kind == "audit":
        verdict = cmd.verdict or "BLOCK"
        notes = cmd.notes or ""
        warrant["auditor_verdict"] = verdict
        warrant["auditor_notes"] = notes

        if verdict == "PASS" and warrant.get("scope_result") == "CLEAN":
            warrant["status"] = "AUDITED"
            if warrant.get("commit_sha"):
                set_commit_status(
                    commit_sha=warrant["commit_sha"],
                    state="pending",
                    description="Auditor PASS. Awaiting merge approval.",
                    target_url=f"http://localhost:3000/w/{warrant_id}",
                )
        else:
            warrant["status"] = "BLOCKED"
            if warrant.get("commit_sha"):
                set_commit_status(
                    commit_sha=warrant["commit_sha"],
                    state="failure",
                    description=f"Auditor BLOCKED: {notes[:80]}",
                    target_url=f"http://localhost:3000/w/{warrant_id}",
                )

        warrant["updated_at"] = now_iso
        warrant["record_hash"] = compute_record_hash(
            prev_hash=warrant["prev_hash"],
            warrant_id=warrant_id,
            plan_hash=warrant.get("plan_hash"),
            diff_hash=warrant.get("diff_hash"),
            scope_result=warrant.get("scope_result", "PENDING"),
            approved_by=warrant.get("approved_by"),
            status=warrant["status"],
        )
        save_warrant(warrant, db_path=db_path)

        save_event(
            event_id=f"evt-{msg_id}-audit",
            warrant_id=warrant_id,
            kind="audit",
            actor=actor,
            msg_id=msg_id,
            excerpt=f"Auditor verdict: {verdict}. {notes}",
            payload={"verdict": verdict, "notes": notes},
            at=timestamp,
            db_path=db_path,
        )
        result["handled"] = True
        result["status"] = warrant["status"]

    # 6. HANDLE MERGE APPROVAL
    elif cmd.kind == "merge":
        authorized, reason = is_approver_authorized(actor)
        if not authorized:
            result["handled"] = False
            result["error"] = f"Unauthorized merge approval: {reason}"
            return result

        # Check preconditions
        if warrant.get("scope_result") != "CLEAN":
            result["handled"] = False
            result["error"] = f"Cannot merge {warrant_id}: Scope check is {warrant.get('scope_result')}."
            return result

        if warrant.get("auditor_verdict") != "PASS":
            result["handled"] = False
            result["error"] = f"Cannot merge {warrant_id}: Auditor verdict is {warrant.get('auditor_verdict')}."
            return result

        # Preconditions met: APPROVE MERGE
        warrant["status"] = "APPROVED_MERGE"
        warrant["updated_at"] = now_iso
        warrant["record_hash"] = compute_record_hash(
            prev_hash=warrant["prev_hash"],
            warrant_id=warrant_id,
            plan_hash=warrant.get("plan_hash"),
            diff_hash=warrant.get("diff_hash"),
            scope_result=warrant["scope_result"],
            approved_by=warrant.get("approved_by"),
            status=warrant["status"],
        )
        save_warrant(warrant, db_path=db_path)

        # Set GitHub status to success
        if warrant.get("commit_sha"):
            set_commit_status(
                commit_sha=warrant["commit_sha"],
                state="success",
                description=f"Warrant {warrant_id} VERIFIED: Plan, scope, and audit approved.",
                target_url=f"http://localhost:3000/w/{warrant_id}",
            )

        # Record file provenance for every touched file
        diff_text = warrant.get("diff_text") or ""
        touched = parse_diff_files(diff_text)
        excerpt = f"Authorized by {warrant.get('approved_by')} in {warrant_id}"
        for f in touched:
            record_file_provenance(
                file_path=f,
                warrant_id=warrant_id,
                commit_sha=warrant.get("commit_sha"),
                status="APPROVED_MERGE",
                approved_by=warrant.get("approved_by"),
                excerpt=excerpt,
                db_path=db_path,
            )

        save_event(
            event_id=f"evt-{msg_id}-merge",
            warrant_id=warrant_id,
            kind="merge",
            actor=actor,
            msg_id=msg_id,
            excerpt=f"Merge approved by {actor}. Status: APPROVED_MERGE",
            payload={"merged_by": actor, "record_hash": warrant["record_hash"]},
            at=timestamp,
            db_path=db_path,
        )
        result["handled"] = True
        result["status"] = "APPROVED_MERGE"
        result["record_hash"] = warrant["record_hash"]

    return result
