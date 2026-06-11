#!/usr/bin/env python3
"""
inbox_sla.py — flag Inbox items older than the SLA threshold.

Usage:
  python3 inbox_sla.py            # default threshold from config (4h)
  python3 inbox_sla.py --hours 8  # override threshold
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

from _config import load_config, vault_subdir


def main():
    cfg = load_config()
    hours = cfg["inbox_sla_hours"]
    if "--hours" in sys.argv:
        hours = int(sys.argv[sys.argv.index("--hours") + 1])

    tz = timezone(timedelta(hours=cfg["timezone_offset_hours"]))
    now = datetime.now(tz)
    threshold = timedelta(hours=hours)
    overdue = []

    inbox = vault_subdir("inbox")
    if not inbox.exists():
        print(f"❌ Inbox dir not found: {inbox}")
        sys.exit(1)

    for f in inbox.glob("*.md"):
        if f.name.startswith("_"):
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz)
        age = now - mtime
        if age > threshold:
            overdue.append((f.name, age))

    if overdue:
        print(f"⚠️ Inbox items older than {hours}h:")
        for name, age in sorted(overdue, key=lambda x: x[1], reverse=True):
            h = age.total_seconds() / 3600
            print(f"  - {name} (sitting {h:.1f}h)")
        sys.exit(1)
    print(f"✅ Inbox all ≤ {hours}h")


if __name__ == "__main__":
    main()
