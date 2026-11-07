"""
Warrant Chat Command and Event Parser.
Parses typed Switch room commands strictly without requiring interactive buttons.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedCommand:
    kind: str  # 'request' | 'plan' | 'approve' | 'build' | 'audit' | 'merge' | 'unknown'
    warrant_id: Optional[str] = None
    plan_hash: Optional[str] = None
    passphrase: Optional[str] = None
    branch: Optional[str] = None
    commit_sha: Optional[str] = None
    diff_text: Optional[str] = None
    verdict: Optional[str] = None  # 'PASS' | 'BLOCK'
    notes: Optional[str] = None
    raw_text: str = ""


# Regex patterns for typed commands in chat (do not span newlines across lines)
SPEAKER_PREFIX_PATTERN = re.compile(r"^\[?[a-zA-Z0-9_\- ]{1,30}\]?:\s*")

APPROVE_PATTERN = re.compile(
    r"^\s*approve\s+(W-[0-9a-zA-Z_\-]+)\s+([0-9a-fA-F]{4,64})(?:\s+([^\s]+))?\s*$",
    re.IGNORECASE,
)

MERGE_PATTERN = re.compile(
    r"^\s*merge\s+(W-[0-9a-zA-Z_\-]+)\s*$",
    re.IGNORECASE,
)

AUDIT_PATTERN = re.compile(
    r"^\s*audit\s+(W-[0-9a-zA-Z_\-]+)\s+(pass|block)(?:\s+(.+))?$",
    re.IGNORECASE | re.DOTALL,
)

BUILD_PATTERN = re.compile(
    r"^\s*built\s+(W-[0-9a-zA-Z_\-]+)\s+branch=([^\s]+)\s+commit=([0-9a-fA-F]{6,40})(?:\s+diff=(.+))?$",
    re.IGNORECASE | re.DOTALL,
)

PLAN_HEADER_PATTERN = re.compile(
    r"(?:Plan for\s+|Warrant:\s*)(W-[0-9a-zA-Z_\-]+)",
    re.IGNORECASE,
)

PLAN_HASH_IN_TEXT_PATTERN = re.compile(
    r"(?:plan hash|hash)\s*:\s*`?([0-9a-fA-F]{4,64})`?",
    re.IGNORECASE,
)

REQUEST_PATTERN = re.compile(
    r"(?:@(?:claude-code|builder|codex|agent)|task\s*:?|warrant\s*:?)\s*(?:\[?(W-[0-9a-zA-Z_\-]+)\]?)?\s*(.*)",
    re.IGNORECASE | re.DOTALL,
)


def parse_chat_message(text: str) -> ParsedCommand:
    """Parses incoming chat message into a structured command."""
    trimmed = text.strip()
    # Strip speaker prefix like "Priya: " or "Claude Code: " if present
    stripped = SPEAKER_PREFIX_PATTERN.sub("", trimmed).strip()
    target = stripped if stripped else trimmed

    # 1. Check typed approval: approve W-014 a3f9c2 [passphrase]
    m_approve = APPROVE_PATTERN.match(target)
    if m_approve:
        return ParsedCommand(
            kind="approve",
            warrant_id=m_approve.group(1).upper(),
            plan_hash=m_approve.group(2).lower(),
            passphrase=m_approve.group(3),
            raw_text=trimmed,
        )

    # 2. Check merge: merge W-014
    m_merge = MERGE_PATTERN.match(target)
    if m_merge:
        return ParsedCommand(
            kind="merge",
            warrant_id=m_merge.group(1).upper(),
            raw_text=trimmed,
        )

    # 3. Check audit verdict: audit W-014 pass [notes]
    m_audit = AUDIT_PATTERN.match(target)
    if m_audit:
        return ParsedCommand(
            kind="audit",
            warrant_id=m_audit.group(1).upper(),
            verdict=m_audit.group(2).upper(),
            notes=m_audit.group(3).strip() if m_audit.group(3) else None,
            raw_text=trimmed,
        )

    # 4. Check build report: built W-014 branch=... commit=... diff=...
    m_build = BUILD_PATTERN.match(target)
    if m_build:
        return ParsedCommand(
            kind="build",
            warrant_id=m_build.group(1).upper(),
            branch=m_build.group(2),
            commit_sha=m_build.group(3),
            diff_text=m_build.group(4),
            raw_text=trimmed,
        )

    # 5. Check if it is a Plan post (e.g. from Builder agent)
    m_plan = PLAN_HEADER_PATTERN.search(target)
    if m_plan:
        w_id = m_plan.group(1).upper()
        h_match = PLAN_HASH_IN_TEXT_PATTERN.search(target)
        p_hash = h_match.group(1).lower() if h_match else None
        return ParsedCommand(
            kind="plan",
            warrant_id=w_id,
            plan_hash=p_hash,
            raw_text=trimmed,
        )

    # 6. Check general request
    m_req = REQUEST_PATTERN.match(target)
    if m_req:
        w_id = m_req.group(1)
        if not w_id:
            w_search = re.search(r"\b(W-[0-9a-zA-Z_\-]+)\b", target)
            if w_search:
                w_id = w_search.group(1)
        if w_id:
            w_id = w_id.upper()
        return ParsedCommand(
            kind="request",
            warrant_id=w_id,
            notes=m_req.group(2).strip(),
            raw_text=trimmed,
        )

    # Fallback: if message mentions W-XXX and is not unknown, treat as request
    w_fallback = re.search(r"\b(W-[0-9a-zA-Z_\-]+)\b", target)
    if w_fallback:
        return ParsedCommand(
            kind="request",
            warrant_id=w_fallback.group(1).upper(),
            notes=target,
            raw_text=trimmed,
        )

    return ParsedCommand(kind="unknown", raw_text=trimmed)
