"""
Warrant GitHub Commit Status Dispatcher.
Posts commit status to GitHub REST API or gracefully skips if unconfigured.
"""

from __future__ import annotations
import json
import os
import urllib.request
import urllib.error
from typing import Any, Dict, Optional


def get_github_config() -> Dict[str, Any]:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    repo = os.getenv("GITHUB_REPO", "").strip()
    is_configured = bool(token and repo and "/" in repo)
    return {
        "is_configured": is_configured,
        "repo": repo if is_configured else None,
        "token_set": bool(token),
    }


def set_commit_status(
    commit_sha: str,
    state: str,  # 'pending' | 'success' | 'failure' | 'error'
    description: str,
    target_url: Optional[str] = None,
    context: str = "warrant/scope-gate",
) -> Dict[str, Any]:
    """
    Sets the commit status on GitHub for the given SHA.
    If GITHUB_TOKEN or GITHUB_REPO is not configured, returns graceful status.
    """
    config = get_github_config()
    if not config["is_configured"]:
        return {
            "status": "not_configured",
            "message": "GitHub status not configured (local/demo mode active)",
            "state": state,
            "commit_sha": commit_sha,
        }

    token = os.getenv("GITHUB_TOKEN", "").strip()
    repo = config["repo"]
    url = f"https://api.github.com/repos/{repo}/statuses/{commit_sha}"

    payload = {
        "state": state,
        "description": description[:140],  # GitHub status description max length is 140
        "context": context,
    }
    if target_url:
        payload["target_url"] = target_url

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Warrant-Clerk-Gatekeeper",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            status_code = resp.getcode()
            return {
                "status": "success",
                "github_status_code": status_code,
                "state": state,
                "commit_sha": commit_sha,
            }
    except urllib.error.HTTPError as err:
        return {
            "status": "failed",
            "github_status_code": err.code,
            "error": err.reason,
            "commit_sha": commit_sha,
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
            "commit_sha": commit_sha,
        }
