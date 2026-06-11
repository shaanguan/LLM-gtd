#!/usr/bin/env python3
"""
cron_heartbeat.py — record cron beats and alert when a job is overdue.

Usage:
  python3 cron_heartbeat.py beat <cron_name>     # mark a successful run
  python3 cron_heartbeat.py check                # report any stale jobs

State file: $GTD_VAULT/.llm-gtd/state/heartbeat.json
Expected jobs and their max-age windows are read from config.yaml
(falls back to built-in defaults in _config.py).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone

from _config import heartbeat_path, load_config


def _tz():
    return timezone(timedelta(hours=load_config()["timezone_offset_hours"]))


def _load() -> dict:
    p = heartbeat_path()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def _save(d: dict) -> None:
    heartbeat_path().write_text(
        json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def beat(name: str) -> None:
    d = _load()
    d[name] = {"last_ok": datetime.now(_tz()).isoformat(timespec="seconds")}
    _save(d)
    print(f"[heartbeat] {name} ok")


def _parse_iso(s: str) -> datetime:
    """datetime.fromisoformat() with timezone support for Python <3.11."""
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        # Python <3.11 can't parse +HH:MM suffix; strip and re-add manually
        if "+" in s[10:]:
            base, tz_part = s.rsplit("+", 1)
            h, m = tz_part.split(":")
            return datetime.fromisoformat(base).replace(
                tzinfo=timezone(timedelta(hours=int(h), minutes=int(m)))
            )
        if s.endswith("Z"):
            return datetime.fromisoformat(s[:-1]).replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(s)


def check() -> None:
    expected = load_config()["cron_expectations"]
    d = _load()
    now = datetime.now(_tz())
    alerts = []
    for name, spec in expected.items():
        last = d.get(name, {}).get("last_ok")
        if not last:
            alerts.append(f"⚠️  {name} ({spec['schedule']}) has never beat")
            continue
        last_dt = _parse_iso(last)
        age_h = (now - last_dt).total_seconds() / 3600
        if age_h > spec["max_age_hours"]:
            alerts.append(
                f"⚠️  {name} ({spec['schedule']}) last beat {age_h:.1f}h ago"
            )
    if alerts:
        print("\n".join(alerts))
        sys.exit(1)
    print("[heartbeat] all cron jobs healthy")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "beat" and len(sys.argv) >= 3:
        beat(sys.argv[2])
    elif cmd == "check":
        check()
    else:
        print(__doc__)
        sys.exit(2)
