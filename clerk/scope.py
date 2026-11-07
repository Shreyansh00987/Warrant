"""
Warrant Scope Checker.
Deterministic verification comparing authorized plan files vs actual git diff files.
Clerk is the enforcer, not an LLM.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Set


@dataclass
class ScopeCheckResult:
    is_clean: bool
    scope_result: str  # 'CLEAN' | 'SCOPE_VIOLATION'
    planned_files: List[str]
    touched_files: List[str]
    offending_files: List[str]
    message: str


def normalize_file_path(path: str) -> str:
    """Normalizes path representation across Windows and POSIX."""
    p = path.strip().replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    return p


def parse_planned_files(plan_md: str) -> List[str]:
    """
    Extracts file paths specified in a plan markdown.
    Recognizes patterns such as:
    - Files: `src/foo.py`, `src/bar.py`
    - Markdown list items: `- src/foo.py` or `* src/foo.py`
    - Fenced file blocks or backticked paths ending with extensions
    """
    if not plan_md:
        return []

    found: Set[str] = set()

    # Match explicitly labelled file sections or bulleted lines
    # e.g., "- `src/invoice/calculator.py`" or "- src/invoice/calculator.py"
    bullet_pattern = re.compile(r"^\s*[-*+]\s+`?([a-zA-Z0-9_\-./]+\.[a-zA-Z0-9]+)`?", re.MULTILINE)
    for m in bullet_pattern.finditer(plan_md):
        found.add(normalize_file_path(m.group(1)))

    # Match paths in backticks with directory separators and extensions: `src/invoice/calculator.py`
    backtick_pattern = re.compile(r"`([a-zA-Z0-9_\-./]+/[a-zA-Z0-9_\-.]+\.[a-zA-Z0-9]+)`")
    for m in backtick_pattern.finditer(plan_md):
        found.add(normalize_file_path(m.group(1)))

    # Match "Files to touch:" or "Target files:" followed by lines
    section_pattern = re.compile(
        r"(?:target files|files touched|files to modify|files)\s*:\s*\n((?:\s*[-*].*\n)+)",
        re.IGNORECASE,
    )
    for section in section_pattern.finditer(plan_md):
        for line in section.group(1).split("\n"):
            m = re.search(r"[-*]\s*`?([a-zA-Z0-9_\-./]+\.[a-zA-Z0-9]+)`?", line)
            if m:
                found.add(normalize_file_path(m.group(1)))

    return sorted(list(found))


def parse_diff_files(diff_text: str) -> List[str]:
    """
    Extracts touched file paths from a standard git unified diff.
    Parses 'diff --git a/... b/...' and '+++ b/...' headers.
    """
    if not diff_text:
        return []

    touched: Set[str] = set()

    # diff --git a/path b/path (allow optional leading whitespace)
    git_diff_pattern = re.compile(r"^\s*diff --git a/(.+?) b/(.+?)$", re.MULTILINE)
    for m in git_diff_pattern.finditer(diff_text):
        path = m.group(2).strip()
        if path != "/dev/null":
            touched.add(normalize_file_path(path))

    # Fallback to +++ b/path (allow optional leading whitespace)
    plus_pattern = re.compile(r"^\s*\+\+\+ (?:b/)?(.+?)$", re.MULTILINE)
    for m in plus_pattern.finditer(diff_text):
        path = m.group(1).strip()
        if path != "/dev/null":
            touched.add(normalize_file_path(path))

    return sorted(list(touched))


def check_scope(planned_files: List[str], touched_files: List[str]) -> ScopeCheckResult:
    """
    Deterministic scope check:
    Every file touched by the agent must be in the approved planned files list.
    TouchedFiles <= PlannedFiles.
    Any touched file not in PlannedFiles is an offending file.
    """
    norm_planned = {normalize_file_path(f) for f in planned_files}
    norm_touched = [normalize_file_path(f) for f in touched_files]

    offending: List[str] = []
    for touched in norm_touched:
        # Check direct match or directory prefix match if directory was granted
        if touched not in norm_planned:
            # Check if plan authorized a directory (e.g. "src/invoice/")
            dir_authorized = any(
                p.endswith("/") and touched.startswith(p) for p in norm_planned
            )
            if not dir_authorized:
                offending.append(touched)

    is_clean = len(offending) == 0
    scope_result = "CLEAN" if is_clean else "SCOPE_VIOLATION"

    if is_clean:
        message = f"Deterministic Scope Check Passed: {len(norm_touched)} touched files all authorized in plan."
    else:
        message = (
            f"SCOPE VIOLATION: {len(offending)} unauthorized file(s) touched: "
            + ", ".join(offending)
        )

    return ScopeCheckResult(
        is_clean=is_clean,
        scope_result=scope_result,
        planned_files=sorted(list(norm_planned)),
        touched_files=norm_touched,
        offending_files=sorted(offending),
        message=message,
    )
