#!/usr/bin/env python3
"""
verify_sync.py — drift detector for vault ↔ Dashboard.

Checks:
  1. frontmatter lint on Next Actions / Waiting For / Projects
  2. duplicate Inbox titles (jaccard bigram similarity)
  3. overdue NA (due < today, still in 02 - Next Actions)
  4. Dashboard freshness (SYNC marker age)

Usage:
  python3 verify_sync.py            # full scan, report to /tmp/gtd-sync-report.md
  python3 verify_sync.py --quick    # vault-only, skip Dashboard freshness
"""

from __future__ import annotations

import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml

from _config import dashboard_path, load_config, vault_subdir

REPORT = Path("/tmp/gtd-sync-report.md")


def _tz():
    return timezone(timedelta(hours=load_config()["timezone_offset_hours"]))


def parse_frontmatter(p: Path):
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)", text, re.DOTALL)
    if not m:
        return None, text, "missing frontmatter"
    try:
        return yaml.safe_load(m.group(1)) or {}, m.group(2), None
    except yaml.YAMLError as e:
        return None, m.group(2), f"YAML error: {e}"


def lint_vault():
    issues = []
    for key in ("next_actions", "waiting_for", "projects"):
        d = vault_subdir(key)
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            if f.name.startswith("_"):
                continue
            fm, _, err = parse_frontmatter(f)
            if err:
                issues.append(f"❌ {d.name}/{f.name}: {err}")
                continue
            if key == "next_actions":
                if not fm.get("due"):
                    issues.append(f"⚠️  {f.name}: missing `due`")
                if not fm.get("project"):
                    issues.append(f"⚠️  {f.name}: missing `project`")
                if not fm.get("priority"):
                    issues.append(f"ℹ️  {f.name}: missing `priority`")
            for k in ("due", "deadline", "date"):
                v = fm.get(k)
                if v and not isinstance(v, (date, datetime)):
                    issues.append(f"⚠️  {f.name}: {k}={v!r} is not a date")
    return issues


def check_dashboard_freshness():
    p = dashboard_path()
    if not p.exists():
        return [f"❌ {p.name} not found"]
    html = p.read_text(encoding="utf-8")
    m = re.search(r"const SYNC='([^']+)'", html)
    if not m:
        return ["❌ Dashboard.html missing SYNC marker"]
    try:
        sync_dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M").replace(tzinfo=_tz())
    except ValueError:
        return [f"❌ malformed SYNC value: {m.group(1)}"]
    age_h = (datetime.now(_tz()) - sync_dt).total_seconds() / 3600
    threshold = load_config()["dashboard_freshness_hours"]
    if age_h > threshold:
        return [f"⚠️  Dashboard {age_h:.1f}h stale (last sync {m.group(1)})"]
    return []


def check_dup_inbox():
    inbox = vault_subdir("inbox")
    if not inbox.exists():
        return []
    files = list(inbox.glob("*.md"))
    titles = []
    for f in files:
        fm, body, _ = parse_frontmatter(f)
        title = (body or "").strip().split("\n")[0][:60]
        titles.append((f.name, title))

    def bigrams(s: str) -> set:
        s = re.sub(r"\s", "", s)
        return {s[i:i + 2] for i in range(len(s) - 1)}

    threshold = load_config()["dup_inbox_jaccard_threshold"]
    issues = []
    for i, (n1, t1) in enumerate(titles):
        for n2, t2 in titles[i + 1:]:
            b1, b2 = bigrams(t1), bigrams(t2)
            if not b1 or not b2:
                continue
            jac = len(b1 & b2) / len(b1 | b2)
            if jac >= threshold:
                issues.append(f"🔁 likely duplicate: {n1} ↔ {n2} (jaccard {jac:.2f})")
    return issues


def check_overdue_unflagged():
    today = datetime.now(_tz()).date()
    issues = []
    na = vault_subdir("next_actions")
    if not na.exists():
        return issues
    for f in na.glob("*.md"):
        if f.name.startswith("_"):
            continue
        fm, _, _ = parse_frontmatter(f)
        if not fm:
            continue
        due = fm.get("due")
        if isinstance(due, str):
            try:
                due = datetime.strptime(due, "%Y-%m-%d").date()
            except ValueError:
                continue
        if isinstance(due, date) and due < today:
            days = (today - due).days
            issues.append(f"📅 {f.name}: overdue by {days} day(s) (due={due})")
    return issues


def main():
    quick = "--quick" in sys.argv
    sections = [
        ("frontmatter lint", lint_vault()),
        ("Inbox dedup", check_dup_inbox()),
        ("overdue NA", check_overdue_unflagged()),
    ]
    if not quick:
        sections.append(("Dashboard freshness", check_dashboard_freshness()))

    lines = [f"# GTD Sync Report — {datetime.now(_tz()):%Y-%m-%d %H:%M}\n"]
    has_issue = False
    for name, items in sections:
        lines.append(f"## {name}")
        if items:
            has_issue = True
            lines.extend(items)
        else:
            lines.append("✅ clean")
        lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    sys.exit(1 if has_issue else 0)


if __name__ == "__main__":
    main()
