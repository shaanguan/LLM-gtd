#!/usr/bin/env python3
"""Shared setup-state helpers for LLM-GTD installers."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


SETUP_STEPS = [
    "detect_repo",
    "ask_preferences",
    "init_vault",
    "install_local_tools",
    "connect_im_docs",
    "verify",
    "onboard",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def state_path(vault: Path) -> Path:
    return vault / ".llm-gtd" / "setup-state.json"


def default_state(vault: Path) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "vault_path": str(vault),
        "updated_at": now_iso(),
        "steps": {step: "pending" for step in SETUP_STEPS},
        "capabilities": {
            "vault": "pending",
            "dashboard": "pending",
            "quickcapture": "pending",
            "scheduler": "pending",
            "im_docs": "pending",
            "git_snapshots": "pending",
            "agent_workspace": "unknown",
        },
        "preferences": {},
        "components": {},
        "next_step": "detect_repo",
    }


def load_setup_state(vault: Path) -> dict[str, Any]:
    path = state_path(vault)
    if not path.is_file():
        return default_state(vault)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = default_state(vault)
        data["components"]["previous_state"] = "unreadable"
    merged = default_state(vault)
    merged.update(data)
    merged["steps"] = {**default_state(vault)["steps"], **data.get("steps", {})}
    merged["capabilities"] = {**default_state(vault)["capabilities"], **data.get("capabilities", {})}
    merged["preferences"] = {**data.get("preferences", {})}
    merged["components"] = {**data.get("components", {})}
    return merged


def first_pending_step(steps: dict[str, str]) -> Optional[str]:
    for step in SETUP_STEPS:
        if steps.get(step) not in {"ok", "skipped"}:
            return step
    return None


def save_setup_state(vault: Path, data: dict[str, Any]) -> dict[str, Any]:
    path = state_path(vault)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["vault_path"] = str(vault)
    data["updated_at"] = now_iso()
    data["next_step"] = first_pending_step(data.get("steps", {})) or "complete"
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data


def update_setup_state(
    vault: Path,
    *,
    steps: Optional[dict[str, str]] = None,
    capabilities: Optional[dict[str, str]] = None,
    preferences: Optional[dict[str, Any]] = None,
    components: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    data = load_setup_state(vault)
    if steps:
        data["steps"].update(steps)
    if capabilities:
        data["capabilities"].update(capabilities)
    if preferences:
        data["preferences"].update(preferences)
    if components:
        data["components"].update(components)
    return save_setup_state(vault, data)
