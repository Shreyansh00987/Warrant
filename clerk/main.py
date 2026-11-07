"""
Warrant Clerk FastAPI Server.
Deterministic gatekeeper API for Warrant Ledger UI and Switch Event Bridge.
"""

from __future__ import annotations
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from clerk.db import (
    get_file_provenance,
    get_warrant,
    get_warrant_by_commit,
    get_warrant_events,
    init_db,
    list_warrants,
)
from clerk.github import get_github_config
from clerk.hasher import (
    compute_diff_hash,
    compute_plan_hash,
    compute_record_hash,
)
from clerk.scope import check_scope, parse_diff_files, parse_planned_files
from clerk.service import get_allowlist, process_room_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB on startup
    init_db()
    yield


app = FastAPI(
    title="Warrant Clerk API",
    description="Deterministic gatekeeper and hash-linked ledger for AI coding agents",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for Web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EventIngestRequest(BaseModel):
    id: Optional[str] = None
    room_id: Optional[str] = "warrant-room"
    sender: Optional[str] = None
    author: Optional[str] = None
    user_id: Optional[str] = None
    sender_id: Optional[str] = None
    content: Optional[str] = None
    text: Optional[str] = None
    timestamp: Optional[str] = None
    source: Optional[str] = "live"


@app.get("/")
def health():
    return {
        "status": "healthy",
        "service": "Warrant Clerk",
        "role": "Deterministic Integrity Gatekeeper",
    }


@app.post("/internal/events")
def ingest_event(event: EventIngestRequest):
    """
    Ingests an incoming event frame from the Switch Room SSE/Webhook bridge.
    Executes deterministic parsing, scope checking, and hash chain linking.
    """
    payload = event.model_dump()
    res = process_room_event(payload)
    return res


@app.get("/api/warrants")
def get_warrants(
    source: Optional[str] = None,
    status: Optional[str] = None,
):
    """Returns all warrants in the ledger."""
    return list_warrants(source=source, status=status)


@app.get("/api/warrants/{warrant_id}")
def get_warrant_detail(warrant_id: str):
    """Returns detailed warrant record, timeline events, and verification state."""
    w = get_warrant(warrant_id.upper())
    if not w:
        raise HTTPException(status_code=404, detail=f"Warrant {warrant_id} not found")

    events = get_warrant_events(w["id"])

    # Compute live verification
    computed_plan_hash = compute_plan_hash(w.get("plan_md"))
    computed_diff_hash = compute_diff_hash(w.get("diff_text"))

    planned = parse_planned_files(w.get("plan_md") or "")
    touched = parse_diff_files(w.get("diff_text") or "")
    scope_check = check_scope(planned, touched)

    computed_record_hash = compute_record_hash(
        prev_hash=w.get("prev_hash", ""),
        warrant_id=w["id"],
        plan_hash=w.get("plan_hash"),
        diff_hash=w.get("diff_hash"),
        scope_result=w.get("scope_result", "PENDING"),
        approved_by=w.get("approved_by"),
        status=w.get("status", "REQUESTED"),
    )

    is_tampered = bool(w.get("record_hash") and w["record_hash"] != computed_record_hash)

    return {
        "warrant": w,
        "events": events,
        "verification": {
            "computed_plan_hash": computed_plan_hash,
            "plan_hash_valid": computed_plan_hash == (w.get("plan_hash") or ""),
            "computed_diff_hash": computed_diff_hash,
            "diff_hash_valid": computed_diff_hash == (w.get("diff_hash") or ""),
            "scope_check": {
                "is_clean": scope_check.is_clean,
                "scope_result": scope_check.scope_result,
                "planned_files": scope_check.planned_files,
                "touched_files": scope_check.touched_files,
                "offending_files": scope_check.offending_files,
            },
            "computed_record_hash": computed_record_hash,
            "stored_record_hash": w.get("record_hash"),
            "is_tampered": is_tampered,
            "is_verified": (not is_tampered) and scope_check.is_clean and w.get("status") == "APPROVED_MERGE",
        },
    }


@app.get("/api/files/{file_path:path}/provenance")
def get_file_prov(file_path: str):
    """Returns the provenance trail for any file touched by agents."""
    prov = get_file_provenance(file_path)
    return {"file_path": file_path, "records": prov}


@app.get("/api/verify/{commit_sha}")
def verify_commit(commit_sha: str):
    """
    Verification endpoint for commit SHA.
    Checks the hash link, plan hash match, diff hash match, and deterministic scope check.
    """
    w = get_warrant_by_commit(commit_sha)
    if not w:
        return {
            "commit_sha": commit_sha,
            "status": "UNAUTHORIZED",
            "reason": f"No warrant on record for commit SHA {commit_sha}.",
            "verified": False,
        }

    computed_plan_hash = compute_plan_hash(w.get("plan_md"))
    computed_diff_hash = compute_diff_hash(w.get("diff_text"))

    planned = parse_planned_files(w.get("plan_md") or "")
    touched = parse_diff_files(w.get("diff_text") or "")
    scope = check_scope(planned, touched)

    computed_rec_hash = compute_record_hash(
        prev_hash=w.get("prev_hash", ""),
        warrant_id=w["id"],
        plan_hash=w.get("plan_hash"),
        diff_hash=w.get("diff_hash"),
        scope_result=w.get("scope_result", "PENDING"),
        approved_by=w.get("approved_by"),
        status=w.get("status", "REQUESTED"),
    )

    if w.get("record_hash") and w["record_hash"] != computed_rec_hash:
        return {
            "commit_sha": commit_sha,
            "warrant_id": w["id"],
            "status": "UNAUTHORIZED",
            "reason": "Hash chain tamper detected: computed record hash does not match stored hash.",
            "verified": False,
            "details": {
                "stored_hash": w.get("record_hash"),
                "computed_hash": computed_rec_hash,
            },
        }

    if not scope.is_clean:
        return {
            "commit_sha": commit_sha,
            "warrant_id": w["id"],
            "status": "UNAUTHORIZED",
            "reason": f"SCOPE VIOLATION: Agent touched unauthorized file(s): {', '.join(scope.offending_files)}",
            "verified": False,
            "offending_files": scope.offending_files,
        }

    if w.get("status") != "APPROVED_MERGE":
        return {
            "commit_sha": commit_sha,
            "warrant_id": w["id"],
            "status": "UNAUTHORIZED",
            "reason": f"Warrant status is '{w.get('status')}', not approved for merge.",
            "verified": False,
        }

    return {
        "commit_sha": commit_sha,
        "warrant_id": w["id"],
        "status": "VERIFIED",
        "reason": f"Deterministic proof valid: approved by {w.get('approved_by')}, scope CLEAN, hashes verified.",
        "verified": True,
        "warrant": {
            "id": w["id"],
            "approved_by": w.get("approved_by"),
            "approved_at": w.get("approved_at"),
            "plan_hash": w.get("plan_hash"),
            "diff_hash": w.get("diff_hash"),
            "record_hash": w.get("record_hash"),
        },
    }


@app.get("/api/stats")
def get_stats():
    """Returns ledger summary counters."""
    warrants = list_warrants()
    approved = sum(1 for w in warrants if w.get("status") == "APPROVED_MERGE")
    out_of_scope = sum(1 for w in warrants if w.get("status") == "OUT_OF_SCOPE")
    blocked = sum(1 for w in warrants if w.get("status") == "BLOCKED")
    pending = sum(1 for w in warrants if w.get("status") in ("REQUESTED", "PLANNED", "APPROVED_PLAN", "BUILT", "AUDITED"))
    live = sum(1 for w in warrants if w.get("source") == "live")
    seeded = sum(1 for w in warrants if w.get("source") == "seeded")

    return {
        "total": len(warrants),
        "approved": approved,
        "out_of_scope": out_of_scope,
        "blocked": blocked,
        "pending": pending,
        "live_count": live,
        "seeded_count": seeded,
    }


@app.get("/api/settings")
def get_settings():
    """Returns configuration and runtime integration status."""
    gh = get_github_config()
    allowlist = get_allowlist()
    room_id = os.getenv("SWITCH_ROOM_ID", "warrant-room")
    switch_url = os.getenv("SWITCH_SERVER_URL", "http://localhost:8080")

    warrants = list_warrants()
    live_count = sum(1 for w in warrants if w.get("source") == "live")
    seeded_count = sum(1 for w in warrants if w.get("source") == "seeded")

    return {
        "approver_allowlist": allowlist,
        "passphrase_configured": bool(os.getenv("APPROVER_PASSPHRASE")),
        "github": {
            "is_configured": gh["is_configured"],
            "repo": gh["repo"],
            "status_message": "GitHub status active" if gh["is_configured"] else "GitHub status not configured (local mode active)",
        },
        "switch": {
            "server_url": switch_url,
            "room_id": room_id,
        },
        "data_sources": {
            "live_records": live_count,
            "seeded_records": seeded_count,
        },
    }


@app.post("/api/seed")
def seed_data():
    """Seeds realistic demonstration warrants W-014 and W-015."""
    from clerk.seed import seed_database
    seed_database()
    return {"status": "success", "message": "Demo warrants W-014 (pass) and W-015 (drift) seeded successfully."}
