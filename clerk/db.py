"""
Warrant Clerk Database Layer.
SQLite backed storage for warrants, events, and audit records.
"""

from __future__ import annotations
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or os.getenv("DATABASE_URL", "sqlite:///./warrant.db").replace("sqlite:///", "")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS warrants (
            id TEXT PRIMARY KEY,
            room_id TEXT NOT NULL,
            request_msg_id TEXT,
            requester TEXT NOT NULL,
            plan_md TEXT,
            plan_hash TEXT,
            approved_by TEXT,
            approved_msg_id TEXT,
            approved_at TEXT,
            branch TEXT,
            commit_sha TEXT,
            diff_text TEXT,
            diff_hash TEXT,
            scope_result TEXT DEFAULT 'PENDING',
            offending_files TEXT DEFAULT '[]',
            auditor_verdict TEXT DEFAULT 'PENDING',
            auditor_notes TEXT,
            status TEXT NOT NULL DEFAULT 'REQUESTED',
            source TEXT NOT NULL DEFAULT 'live',
            prev_hash TEXT NOT NULL DEFAULT '0000000000000000000000000000000000000000000000000000000000000000',
            record_hash TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            warrant_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            actor TEXT NOT NULL,
            msg_id TEXT,
            excerpt TEXT NOT NULL,
            payload TEXT NOT NULL,
            at TEXT NOT NULL,
            FOREIGN KEY (warrant_id) REFERENCES warrants (id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS file_provenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            warrant_id TEXT NOT NULL,
            commit_sha TEXT,
            status TEXT NOT NULL,
            approved_by TEXT,
            excerpt TEXT,
            at TEXT NOT NULL,
            FOREIGN KEY (warrant_id) REFERENCES warrants (id)
        )
        """
    )

    # Indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_warrants_commit ON warrants(commit_sha)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_warrant ON events(warrant_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_file_prov_path ON file_provenance(file_path)")

    conn.commit()
    conn.close()


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    d = dict(row)
    if "offending_files" in d and isinstance(d["offending_files"], str):
        try:
            d["offending_files"] = json.loads(d["offending_files"])
        except Exception:
            d["offending_files"] = []
    return d


def get_warrant(warrant_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM warrants WHERE id = ?", (warrant_id,))
    row = cur.fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def get_warrant_by_commit(commit_sha: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM warrants WHERE commit_sha = ? ORDER BY updated_at DESC LIMIT 1", (commit_sha,))
    row = cur.fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def get_last_warrant(db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM warrants ORDER BY rowid DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def list_warrants(
    source: Optional[str] = None,
    status: Optional[str] = None,
    db_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    query = "SELECT * FROM warrants WHERE 1=1"
    params: List[Any] = []
    if source and isinstance(source, str):
        query += " AND source = ?"
        params.append(source)
    if status and isinstance(status, str):
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY rowid DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def get_warrant_events(warrant_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM events WHERE warrant_id = ? ORDER BY at ASC", (warrant_id,))
    rows = cur.fetchall()
    conn.close()
    res = []
    for r in rows:
        d = dict(r)
        try:
            d["payload"] = json.loads(d["payload"])
        except Exception:
            pass
        res.append(d)
    return res


def save_warrant(warrant_data: Dict[str, Any], db_path: Optional[str] = None) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()

    offending = warrant_data.get("offending_files", [])
    if isinstance(offending, list):
        offending_str = json.dumps(offending)
    else:
        offending_str = str(offending)

    cur.execute(
        """
        INSERT INTO warrants (
            id, room_id, request_msg_id, requester, plan_md, plan_hash,
            approved_by, approved_msg_id, approved_at, branch, commit_sha,
            diff_text, diff_hash, scope_result, offending_files,
            auditor_verdict, auditor_notes, status, source,
            prev_hash, record_hash, created_at, updated_at
        ) VALUES (
            :id, :room_id, :request_msg_id, :requester, :plan_md, :plan_hash,
            :approved_by, :approved_msg_id, :approved_at, :branch, :commit_sha,
            :diff_text, :diff_hash, :scope_result, :offending_files,
            :auditor_verdict, :auditor_notes, :status, :source,
            :prev_hash, :record_hash, :created_at, :updated_at
        )
        ON CONFLICT(id) DO UPDATE SET
            room_id = excluded.room_id,
            request_msg_id = COALESCE(excluded.request_msg_id, warrants.request_msg_id),
            requester = excluded.requester,
            plan_md = COALESCE(excluded.plan_md, warrants.plan_md),
            plan_hash = COALESCE(excluded.plan_hash, warrants.plan_hash),
            approved_by = COALESCE(excluded.approved_by, warrants.approved_by),
            approved_msg_id = COALESCE(excluded.approved_msg_id, warrants.approved_msg_id),
            approved_at = COALESCE(excluded.approved_at, warrants.approved_at),
            branch = COALESCE(excluded.branch, warrants.branch),
            commit_sha = COALESCE(excluded.commit_sha, warrants.commit_sha),
            diff_text = COALESCE(excluded.diff_text, warrants.diff_text),
            diff_hash = COALESCE(excluded.diff_hash, warrants.diff_hash),
            scope_result = excluded.scope_result,
            offending_files = excluded.offending_files,
            auditor_verdict = excluded.auditor_verdict,
            auditor_notes = COALESCE(excluded.auditor_notes, warrants.auditor_notes),
            status = excluded.status,
            source = excluded.source,
            prev_hash = excluded.prev_hash,
            record_hash = excluded.record_hash,
            updated_at = excluded.updated_at
        """,
        {
            "id": warrant_data["id"],
            "room_id": warrant_data.get("room_id", "default-room"),
            "request_msg_id": warrant_data.get("request_msg_id"),
            "requester": warrant_data.get("requester", "unknown"),
            "plan_md": warrant_data.get("plan_md"),
            "plan_hash": warrant_data.get("plan_hash"),
            "approved_by": warrant_data.get("approved_by"),
            "approved_msg_id": warrant_data.get("approved_msg_id"),
            "approved_at": warrant_data.get("approved_at"),
            "branch": warrant_data.get("branch"),
            "commit_sha": warrant_data.get("commit_sha"),
            "diff_text": warrant_data.get("diff_text"),
            "diff_hash": warrant_data.get("diff_hash"),
            "scope_result": warrant_data.get("scope_result", "PENDING"),
            "offending_files": offending_str,
            "auditor_verdict": warrant_data.get("auditor_verdict", "PENDING"),
            "auditor_notes": warrant_data.get("auditor_notes"),
            "status": warrant_data.get("status", "REQUESTED"),
            "source": warrant_data.get("source", "live"),
            "prev_hash": warrant_data.get("prev_hash", "0" * 64),
            "record_hash": warrant_data.get("record_hash", ""),
            "created_at": warrant_data.get("created_at", datetime.now(timezone.utc).isoformat()),
            "updated_at": warrant_data.get("updated_at", datetime.now(timezone.utc).isoformat()),
        },
    )
    conn.commit()
    conn.close()


def save_event(
    event_id: str,
    warrant_id: str,
    kind: str,
    actor: str,
    msg_id: Optional[str],
    excerpt: str,
    payload: Dict[str, Any],
    at: Optional[str] = None,
    db_path: Optional[str] = None,
) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO events (id, warrant_id, kind, actor, msg_id, excerpt, payload, at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            warrant_id,
            kind,
            actor,
            msg_id,
            excerpt,
            json.dumps(payload),
            at or datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def record_file_provenance(
    file_path: str,
    warrant_id: str,
    commit_sha: Optional[str],
    status: str,
    approved_by: Optional[str],
    excerpt: Optional[str],
    db_path: Optional[str] = None,
) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO file_provenance (file_path, warrant_id, commit_sha, status, approved_by, excerpt, at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            file_path,
            warrant_id,
            commit_sha,
            status,
            approved_by,
            excerpt,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_file_provenance(file_path: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    # Normalize path slashes
    norm_path = file_path.replace("\\", "/")
    cur.execute(
        """
        SELECT fp.*, w.requester, w.plan_hash, w.diff_hash, w.scope_result
        FROM file_provenance fp
        JOIN warrants w ON fp.warrant_id = w.id
        WHERE fp.file_path = ? OR fp.file_path LIKE ?
        ORDER BY fp.at DESC
        """,
        (norm_path, f"%{norm_path}"),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
