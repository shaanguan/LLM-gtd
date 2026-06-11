#!/usr/bin/env python3
"""
preflight.py — environment self-check executed before each cron job.

Checks:
  1. PTO flag (if $GTD_VAULT/.gtd-workbench/state/pto exists, skip cron body)
  2. vault directory readable
  3. python3 yaml package available

Usage:
  python3 preflight.py            # exit 0 ok / 1 fail / 2 skip (PTO)
  python3 preflight.py --pto-on   # turn on pause flag
  python3 preflight.py --pto-off  # turn off pause flag
"""

from __future__ import annotations

import sys

from _config import get_vault, pto_flag_path


def main():
    if "--pto-on" in sys.argv:
        p = pto_flag_path()
        p.write_text("paused\n", encoding="utf-8")
        print(f"✅ PTO on, cron jobs will skip ({p})")
        return
    if "--pto-off" in sys.argv:
        p = pto_flag_path()
        if p.exists():
            p.unlink()
        print("✅ PTO off, cron jobs resume")
        return

    if pto_flag_path().exists():
        print("⏸  PTO active, skipping cron body")
        sys.exit(2)

    vault = get_vault()
    if not vault.exists():
        print(f"❌ vault unreachable: {vault}")
        sys.exit(1)

    try:
        import yaml  # noqa: F401
    except ImportError:
        print("❌ python yaml unavailable — pip install pyyaml")
        sys.exit(1)

    print("✅ preflight ok")


if __name__ == "__main__":
    main()
