#!/usr/bin/env python3
"""Version helpers and remote release checks for LLM-GTD."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parent.parent
GITHUB_REPO = "shaanguan/LLM-gtd"
VERSION_FILE = REPO_ROOT / "VERSION"
RELEASES_LATEST_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def normalize_version(value: str) -> str:
    value = value.strip()
    if value.startswith("v"):
        value = value[1:]
    return value


def parse_version(value: str) -> tuple[int, int, int]:
    cleaned = normalize_version(value)
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", cleaned)
    if not match:
        raise ValueError(f"Invalid semver: {value}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def compare_versions(left: str, right: str) -> int:
    """Return -1 if left < right, 0 if equal, 1 if left > right."""
    a = parse_version(left)
    b = parse_version(right)
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def read_repo_version() -> str:
    if VERSION_FILE.is_file():
        text = VERSION_FILE.read_text(encoding="utf-8").strip()
        if text:
            return normalize_version(text)
    return "0.0.0"


def read_vault_version(vault: Path) -> Optional[str]:
    version_file = vault / ".llm-gtd" / "version"
    if not version_file.is_file():
        return None
    return normalize_version(version_file.read_text(encoding="utf-8"))


def fetch_latest_release_tag(timeout: float = 8.0) -> tuple[Optional[str], Optional[str]]:
    request = urllib.request.Request(
        RELEASES_LATEST_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "llm-gtd-upgrade",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return None, f"GitHub API HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return None, f"Network error: {exc.reason}"
    except Exception as exc:
        return None, str(exc)

    tag = payload.get("tag_name")
    if not tag:
        return None, "Missing tag_name in GitHub release payload"
    return str(tag), None


def check_for_updates(
    *,
    local_repo_version: Optional[str] = None,
    vault_version: Optional[str] = None,
    fetch_remote: bool = True,
) -> dict:
    repo_version = normalize_version(local_repo_version or read_repo_version())
    result = {
        "repo_version": repo_version,
        "vault_version": normalize_version(vault_version) if vault_version else None,
        "remote_version": None,
        "remote_tag": None,
        "repo_behind_remote": None,
        "vault_behind_repo": None,
        "update_available": False,
        "error": None,
    }

    if vault_version is not None:
        try:
            result["vault_behind_repo"] = compare_versions(vault_version, repo_version) < 0
        except ValueError:
            result["vault_behind_repo"] = True

    if not fetch_remote:
        result["update_available"] = bool(result.get("vault_behind_repo"))
        return result

    remote_tag, error = fetch_latest_release_tag()
    if error:
        result["error"] = error
        result["update_available"] = bool(result.get("vault_behind_repo"))
        return result

    remote_version = normalize_version(remote_tag)
    result["remote_tag"] = remote_tag
    result["remote_version"] = remote_version
    try:
        result["repo_behind_remote"] = compare_versions(repo_version, remote_version) < 0
    except ValueError:
        result["repo_behind_remote"] = True

    result["update_available"] = bool(
        result.get("vault_behind_repo")
        or result.get("repo_behind_remote")
    )
    return result
