"""
Warrant Hasher.
Deterministic SHA-256 hashing for plan content, git diffs, and the hash chain.
"""

from __future__ import annotations
import hashlib
from typing import Optional

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"


def normalize_text(text: Optional[str]) -> str:
    """
    Normalizes text for consistent hashing across platforms:
    - Replaces CRLF (\r\n) with LF (\n).
    - Strips leading and trailing whitespace.
    - Strips trailing whitespace on each line.
    """
    if not text:
        return ""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    cleaned_lines = [line.rstrip() for line in lines]
    return "\n".join(cleaned_lines).strip()


def compute_plan_hash(plan_md: Optional[str]) -> str:
    """Computes SHA-256 hash of normalized plan markdown."""
    normalized = normalize_text(plan_md)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_diff_hash(diff_text: Optional[str]) -> str:
    """Computes SHA-256 hash of normalized git diff/patch content."""
    normalized = normalize_text(diff_text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_record_hash(
    prev_hash: str,
    warrant_id: str,
    plan_hash: Optional[str],
    diff_hash: Optional[str],
    scope_result: str,
    approved_by: Optional[str],
    status: str,
) -> str:
    """
    Computes the hash-linked record hash:
    SHA-256(prev_hash || warrant_id || plan_hash || diff_hash || scope_result || approved_by || status)
    """
    p_hash = prev_hash or GENESIS_HASH
    pl_hash = plan_hash or ""
    d_hash = diff_hash or ""
    scope = scope_result or "PENDING"
    approver = approved_by or "unapproved"
    stat = status or "PENDING"

    payload = f"{p_hash}:{warrant_id}:{pl_hash}:{d_hash}:{scope}:{approver}:{stat}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def matches_plan_hash(full_hash: Optional[str], candidate: str) -> bool:
    """
    Checks if a candidate approval hash (prefix or full) matches the computed plan hash.
    Case-insensitive matching.
    """
    if not full_hash or not candidate:
        return False
    cand = candidate.strip().lower()
    fh = full_hash.strip().lower()
    return fh.startswith(cand) or fh == cand
