#!/usr/bin/env python3
"""Component manifest and state helpers for LLM-GTD upgrades."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from state import now_iso
from version import REPO_ROOT, read_repo_version


MANIFEST_PATH = REPO_ROOT / "tools" / "setup" / "components.json"


def component_state_path(vault: Path) -> Path:
    return vault / ".llm-gtd" / "component-state.json"


def load_manifest(repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    path = repo_root / "tools" / "setup" / "components.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return sorted(data, key=lambda item: item["id"])


def _expand_one(repo_root: Path, pattern: str) -> list[Path]:
    matches: list[Path] = []
    if any(char in pattern for char in "*?["):
        matches = [path for path in repo_root.glob(pattern) if path.is_file()]
    else:
        path = repo_root / pattern
        if path.is_dir():
            matches = [child for child in path.rglob("*") if child.is_file()]
        elif path.is_file():
            matches = [path]
    return sorted(matches, key=lambda path: path.relative_to(repo_root).as_posix())


def source_files(component: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[Path]:
    files: list[Path] = []
    seen: set[str] = set()
    for pattern in component.get("source_paths", []):
        for path in _expand_one(repo_root, pattern):
            rel = path.relative_to(repo_root).as_posix()
            if rel not in seen:
                files.append(path)
                seen.add(rel)
    return sorted(files, key=lambda path: path.relative_to(repo_root).as_posix())


def component_hash(component: dict[str, Any], repo_root: Path = REPO_ROOT) -> str:
    digest = hashlib.sha256()
    digest.update(component["id"].encode("utf-8"))
    digest.update(b"\0")
    for path in source_files(component, repo_root):
        rel = path.relative_to(repo_root).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def load_component_state(vault: Path) -> dict[str, Any]:
    path = component_state_path(vault)
    if not path.is_file():
        return {"schema_version": 1, "components": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"schema_version": 1, "components": {}, "previous_state": "unreadable"}
    data.setdefault("schema_version", 1)
    data.setdefault("components", {})
    return data


def save_component_state(vault: Path, data: dict[str, Any]) -> dict[str, Any]:
    path = component_state_path(vault)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["schema_version"] = 1
    data["updated_at"] = now_iso()
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data


def mark_component_applied(
    vault: Path,
    component: dict[str, Any],
    source_hash: str,
    *,
    status: str = "ok",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = load_component_state(vault)
    entry = {
        "id": component["id"],
        "layer": component["layer"],
        "source_hash": source_hash,
        "applied_at": now_iso(),
        "repo_version": read_repo_version(),
        "status": status,
    }
    if details:
        entry["details"] = details
    data["components"][component["id"]] = entry
    return save_component_state(vault, data)


def current_component_status(
    vault: Path,
    repo_root: Path = REPO_ROOT,
    *,
    selected_ids: set[str] | None = None,
    force: bool = False,
) -> list[dict[str, Any]]:
    state = load_component_state(vault)
    previous = state.get("components", {})
    rows: list[dict[str, Any]] = []
    for component in load_manifest(repo_root):
        if selected_ids is not None and component["id"] not in selected_ids:
            continue
        current_hash = component_hash(component, repo_root)
        applied_hash = previous.get(component["id"], {}).get("source_hash")
        changed = force or applied_hash != current_hash
        rows.append({
            "id": component["id"],
            "layer": component["layer"],
            "changed": changed,
            "current_hash": current_hash,
            "applied_hash": applied_hash,
            "action": component.get("action"),
            "apply_mode": component.get("apply_mode"),
            "target": component.get("target"),
        })
    return rows
