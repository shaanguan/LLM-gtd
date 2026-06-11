"""
llm-gtd shared config loader.

Resolution order:
  1. $GTD_VAULT env var (path to vault root) — required
  2. $GTD_VAULT/.llm-gtd/config.yaml — optional overrides
  3. Built-in defaults (this file)

State files (heartbeat / PTO flag) live under $GTD_VAULT/.llm-gtd/state/
so they travel with the vault when synced (Dropbox/iCloud) and never leak into
arbitrary $HOME paths.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # config.yaml is optional


DEFAULTS: Dict[str, Any] = {
    "vault_dirs": {
        "inbox": "00 - Inbox",
        "projects": "01 - Projects",
        "next_actions": "02 - Next Actions",
        "waiting_for": "03 - Waiting For",
        "someday": "04 - Someday Maybe",
        "reference": "05 - Reference",
        "archive": "06 - Archive",
        "achievements": "07 - Achievements",
        "templates": "Templates",
    },
    "dashboard_file": "Dashboard.html",
    "timezone_offset_hours": 8,
    "cron_expectations": {
        "morning":   {"max_age_hours": 26,    "schedule": "10:30 daily"},
        "evening":   {"max_age_hours": 26,    "schedule": "22:30 daily"},
        "daily_doc": {"max_age_hours": 26,    "schedule": "22:00 daily"},
        "weekly":    {"max_age_hours": 7*24+2, "schedule": "Fri 18:30"},
        "git_snap":  {"max_age_hours": 26,    "schedule": "23:55 daily"},
    },
    "inbox_sla_hours": 4,
    "dashboard_freshness_hours": 12,
    "dup_inbox_jaccard_threshold": 0.4,
}


def get_vault() -> Path:
    """Resolve vault root from $GTD_VAULT. Exit with clear error if missing."""
    raw = os.environ.get("GTD_VAULT")
    if not raw:
        sys.stderr.write(
            "ERROR: $GTD_VAULT is not set.\n"
            "  Point it to your Obsidian vault, e.g.:\n"
            '    export GTD_VAULT="$HOME/Documents/my-gtd-vault"\n'
        )
        sys.exit(2)
    p = Path(os.path.expanduser(raw)).resolve()
    if not p.exists():
        sys.stderr.write(f"ERROR: $GTD_VAULT does not exist: {p}\n")
        sys.exit(2)
    return p


def state_dir() -> Path:
    """Return $GTD_VAULT/.llm-gtd/state, creating it if needed."""
    d = get_vault() / ".llm-gtd" / "state"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config() -> Dict[str, Any]:
    """Defaults merged with optional $GTD_VAULT/.llm-gtd/config.yaml."""
    cfg = dict(DEFAULTS)
    cfg_path = get_vault() / ".llm-gtd" / "config.yaml"
    if cfg_path.exists() and yaml is not None:
        try:
            user = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            cfg = _deep_merge(cfg, user)
        except Exception as e:
            sys.stderr.write(f"WARNING: failed to parse {cfg_path}: {e}\n")
    return cfg


def vault_subdir(key: str) -> Path:
    """E.g. vault_subdir('next_actions') -> $GTD_VAULT/02 - Next Actions"""
    cfg = load_config()
    name = cfg["vault_dirs"][key]
    return get_vault() / name


def dashboard_path() -> Path:
    return get_vault() / load_config()["dashboard_file"]


def pto_flag_path() -> Path:
    return state_dir() / "pto"


def heartbeat_path() -> Path:
    return state_dir() / "heartbeat.json"
