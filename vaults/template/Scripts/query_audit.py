#!/usr/bin/env python3
"""Append query evidence audits for LLM-GTD answers.

This is intentionally small: it records which vault evidence backed a
state-bearing answer without becoming a second source of truth.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _config import get_vault


def _many(values: list[str] | None) -> list[str]:
    return [value for value in (values or []) if value]


def audit_path(vault: Path) -> Path:
    return vault / ".llm-gtd" / "logs" / "query-audit.jsonl"


def append_entry(vault: Path, entry: dict[str, Any]) -> Path:
    path = audit_path(vault)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def build_entry(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query_type": args.query_type,
        "evidence_paths": _many(args.evidence),
        "missing_facts": _many(args.missing),
        "answer_mode": args.mode,
        "suggested_compounding_target": args.suggested_compounding_target or "",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Append an LLM-GTD query audit entry")
    parser.add_argument("--type", dest="query_type", required=True, help="Query class, e.g. status, prioritization, sync")
    parser.add_argument("--mode", required=True, help="Answer mode, e.g. vault-evidence, mixed, methodology")
    parser.add_argument("--evidence", action="append", help="Vault path used as evidence; repeatable")
    parser.add_argument("--missing", action="append", help="Missing fact disclosed in the answer; repeatable")
    parser.add_argument("--suggested-compounding-target", default="", help="Optional Project/Reference/wiki target suggested to user")
    args = parser.parse_args()

    path = append_entry(get_vault(), build_entry(args))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
