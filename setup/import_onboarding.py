#!/usr/bin/env python3
"""
import_onboarding.py — Import 7-day onboarding tasks into user's vault Inbox.

Replaces template placeholders ({{day1}} through {{day7}}, {{config.rendered_at}})
with actual dates starting from today.

Usage:
    python3 import_onboarding.py --vault /path/to/vault --repo /path/to/llm-gtd
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Import 7-day onboarding tasks")
    parser.add_argument("--vault", required=True, help="User vault path")
    parser.add_argument("--repo", required=True, help="LLM-GTD repo path")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    repo = Path(args.repo).expanduser().resolve()

    inbox_template = repo / "vault-template" / "00 - Inbox"
    inbox_dest = vault / "00 - Inbox"
    inbox_dest.mkdir(parents=True, exist_ok=True)

    today = datetime.now()
    now_str = today.strftime("%Y-%m-%d %H:%M")

    # Build replacement map
    replacements = {
        "{{config.rendered_at}}": now_str,
    }
    for i in range(1, 8):
        day_date = today + timedelta(days=i - 1)
        replacements[f"{{{{day{i}}}}}"] = day_date.strftime("%Y-%m-%d")

    # Find Day N files
    day_files = sorted(inbox_template.glob("Day *.md"))
    if not day_files:
        print("[!] No Day files found in vault-template/00 - Inbox/")
        return 1

    count = 0
    for src in day_files:
        content = src.read_text(encoding="utf-8")
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        dest = inbox_dest / src.name
        dest.write_text(content, encoding="utf-8")
        count += 1
        print(f"  [+] {src.name} -> due: {content.split('due: ')[1].split(chr(10))[0] if 'due: ' in content else '?'}")

    print(f"\n  Imported {count} onboarding tasks into {inbox_dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
