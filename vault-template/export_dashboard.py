#!/usr/bin/env python3
"""
export_dashboard.py — vault → Dashboard.html data sync

Scans the four data directories (Projects / Next Actions / Waiting For /
Achievements) and injects DATA + SYNC + VBASE + optional OKR/WEEKS into
Dashboard.html. Replaces only the data lines; the rest of the document
(CSS / DOM / JS logic) stays untouched.

Usage: python3 export_dashboard.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent / "Scripts"))
from _config import (  # type: ignore  # noqa: E402
    dashboard_path,
    get_vault,
    load_config,
    vault_subdir,
)


def _tz():
    return timezone(timedelta(hours=load_config()["timezone_offset_hours"]))


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)", text, re.DOTALL)
    if not m:
        print(f"[warn] {path.name}: missing frontmatter", file=sys.stderr)
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        print(f"[error] {path.name}: YAML parse failed: {e}", file=sys.stderr)
        fm = {}
    return fm, m.group(2)


def extract_title(fm: dict, body: str, filename: str) -> str:
    if fm.get("title"):
        return fm["title"]
    heading = re.search(r"^##\s+(.+)", body, re.MULTILINE)
    if heading:
        return heading.group(1).strip()
    name = filename.replace(".md", "")
    name = re.sub(r"^\d{8}[-\s]*\d*\s*", "", name)
    return name


def is_side_project(fm: dict) -> bool:
    """Side-project / personal cards — shown in the dimmed `bl` section."""
    project = fm.get("project") or ""
    side_prefix = load_config().get("side_project_prefix", "")
    if side_prefix and project.startswith(side_prefix):
        return True
    tags = fm.get("tags") or []
    return "side-project" in tags


def build_item(path: Path, item_type: str) -> dict:
    fm, body = parse_frontmatter(path)
    return {
        "fn": path.stem,
        "title": extract_title(fm, body, path.name),
        "type": item_type,
        "project": fm.get("project", "") or "",
        "due": str(fm.get("due", "") or ""),
        "deadline": str(fm.get("deadline", "") or ""),
        "priority": fm.get("priority", "") or "",
        "okr": fm.get("okr", "") or "",
        "owner": fm.get("owner", "") or "",
        "date": str(fm.get("date", "") or ""),
        "bl": is_side_project(fm),
    }


def scan(item_type: str, dir_key: str) -> list[dict]:
    d = vault_subdir(dir_key)
    if not d.exists():
        return []
    items = []
    for f in sorted(d.glob("*.md")):
        if f.name.startswith("_"):
            continue
        items.append(build_item(f, item_type))
    return items


def load_okr_config() -> dict:
    """Optional OKR config at $GTD_VAULT/05 - Reference/okr.yaml."""
    p = vault_subdir("reference") / "okr.yaml"
    if not p.exists():
        return {"ON": {}, "OC": {}, "milestone": None}
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        print(f"[warn] okr.yaml parse failed: {e}", file=sys.stderr)
        return {"ON": {}, "OC": {}, "milestone": None}
    return {
        "ON": data.get("labels", {}) or {},
        "OC": data.get("colors", {}) or {},
        "milestone": data.get("milestone") or None,
    }


def load_weeks() -> dict:
    """Optional weekly digest at $GTD_VAULT/05 - Reference/weeks.yaml."""
    p = vault_subdir("reference") / "weeks.yaml"
    if not p.exists():
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        print(f"[warn] weeks.yaml parse failed: {e}", file=sys.stderr)
        return {}


def inject(data: list[dict], sync_time: str, okr: dict, weeks: dict) -> None:
    p = dashboard_path()
    html = p.read_text(encoding="utf-8")

    def replace_const(name: str, value: str, src: str) -> str:
        # match `const NAME=…;` up to the first standalone `;` at end of line
        pattern = rf"const {name}=.*?;(?=\s*\n)"
        return re.sub(pattern, f"const {name}={value};", src, count=1, flags=re.DOTALL)

    html = replace_const("DATA", json.dumps(data, ensure_ascii=False, separators=(",", ":")), html)
    html = replace_const("SYNC", f"'{sync_time}'", html)
    html = replace_const("VBASE", f"'{get_vault()}'", html)
    html = replace_const("OKR", json.dumps(okr, ensure_ascii=False, separators=(",", ":")), html)
    html = replace_const("WEEKS", json.dumps(weeks, ensure_ascii=False, separators=(",", ":")), html)

    p.write_text(html, encoding="utf-8")


def main():
    data = []
    for item_type, dir_key in [
        ("proj", "projects"),
        ("na", "next_actions"),
        ("wf", "waiting_for"),
        ("ach", "achievements"),
    ]:
        data.extend(scan(item_type, dir_key))

    sync_time = datetime.now(_tz()).strftime("%Y-%m-%d %H:%M")
    okr = load_okr_config()
    weeks = load_weeks()

    inject(data, sync_time, okr, weeks)

    counts: dict[str, int] = {}
    for item in data:
        counts[item["type"]] = counts.get(item["type"], 0) + 1
    print(f"[export_dashboard] synced @ {sync_time}")
    print(f"  projects:     {counts.get('proj', 0)}")
    print(f"  next actions: {counts.get('na', 0)}")
    print(f"  waiting for:  {counts.get('wf', 0)}")
    print(f"  achievements: {counts.get('ach', 0)}")
    print(f"  total:        {len(data)} items")


if __name__ == "__main__":
    main()
