#!/usr/bin/env python3
"""
llm-gtd interactive initializer.

Usage:
    python3 setup/init.py [--vault PATH]

Walks you through 3 questions, renders vault-template/ into your vault,
and prints cron-registration guidance for QoderWork.
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "vault-template"
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"

DEFAULT_TIMEZONE = "Asia/Shanghai"
DEFAULT_MORNING = "10:30"
DEFAULT_EVENING = "22:30"
DEFAULT_WEEKLY = "Sun 21:00"

FEATURES_ALL = ["okr", "dingtalk", "side_project", "knowledge_base"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def ask(prompt: str, default: str = "") -> str:
    """Prompt user for input with optional default."""
    suffix = f" [{default}]" if default else ""
    answer = input(f"{prompt}{suffix}: ").strip()
    return answer if answer else default


def ask_yn(prompt: str, default: bool = True) -> bool:
    """Yes/no question."""
    hint = "Y/n" if default else "y/N"
    answer = input(f"{prompt} [{hint}]: ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes")


def render_conditionals(text: str, features: dict) -> str:
    """
    Process <!-- IF feature.X --> ... <!-- ELSE --> ... <!-- ENDIF --> blocks.
    """
    # Pattern: <!-- IF feature.xxx --> ... (<!-- ELSE --> ...)? <!-- ENDIF -->
    pattern = re.compile(
        r'<!-- IF feature\.(\w+) -->\s*\n(.*?)(?:<!-- ELSE -->\s*\n(.*?))?<!-- ENDIF -->\s*\n',
        re.DOTALL,
    )

    def replacer(m):
        feat = m.group(1)
        if_block = m.group(2)
        else_block = m.group(3) or ""
        if features.get(feat, False):
            return if_block
        else:
            return else_block

    return pattern.sub(replacer, text)


def render_placeholders(text: str, variables: dict) -> str:
    """Replace {{key.subkey}} placeholders with values from a flat dict."""
    def replacer(m):
        key = m.group(1)
        return variables.get(key, m.group(0))  # keep unresolved as-is

    return re.compile(r'\{\{([a-z_][a-z0-9_.]*)\}\}').sub(replacer, text)


def copy_template(template_dir: Path, dest: Path, skip_agents: bool = True):
    """
    Recursively copy vault-template/ to dest, skipping AGENTS.md
    (which gets rendered separately) and .gitkeep files.
    """
    for src_path in sorted(template_dir.rglob("*")):
        rel = src_path.relative_to(template_dir)

        # Skip AGENTS.md — we render it with variables
        if skip_agents and rel.name == "AGENTS.md":
            continue

        # Skip .gitkeep — they are repo scaffolding only
        if rel.name == ".gitkeep":
            continue

        dest_path = dest / rel

        if src_path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
        else:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            if not dest_path.exists():
                shutil.copy2(src_path, dest_path)
            else:
                # Don't overwrite user files
                pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Initialize a GTD Workbench vault")
    parser.add_argument("--vault", type=str, help="Target vault path (skip interactive question)")
    parser.add_argument("--non-interactive", action="store_true", help="Use all defaults")
    args = parser.parse_args()

    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   GTD Workbench — Interactive Setup          ║")
    print("║   Your AI GTD secretary, powered by QoderWork║")
    print("╚══════════════════════════════════════════════╝")
    print()

    # ── Question 1: Vault path ──────────────────────────────────────────
    if args.vault:
        vault_path = Path(args.vault).expanduser().resolve()
    elif args.non_interactive:
        vault_path = Path.home() / "Documents" / "GTD"
    else:
        default_vault = os.environ.get("GTD_VAULT", str(Path.home() / "Documents" / "GTD"))
        raw = ask("1/3  Where should we create your vault?", default_vault)
        vault_path = Path(raw).expanduser().resolve()

    print(f"     → Vault: {vault_path}")
    print()

    # ── Question 2: Features ────────────────────────────────────────────
    features = {
        "okr": True,
        "dingtalk": True,
        "side_project": False,
        "knowledge_base": True,
    }

    if not args.non_interactive:
        features["okr"] = ask_yn("2/3  Enable OKR tracking? (links NAs to objectives)", True)
        features["dingtalk"] = ask_yn("     Enable DingTalk document sync?", True)
        features["side_project"] = ask_yn("     Track a personal side project (separate from work)?", False)
        features["knowledge_base"] = ask_yn("     Include GTD knowledge base references in AGENTS.md?", True)
        print()

    # ── Question 3: Cron schedule ───────────────────────────────────────
    if not args.non_interactive:
        morning_time = ask("3/3  Morning brief cron time (HH:MM)", DEFAULT_MORNING)
        evening_time = ask("     Evening review cron time (HH:MM)", DEFAULT_EVENING)
        weekly_time = ask("     Weekly review (e.g. 'Sun 21:00')", DEFAULT_WEEKLY)
    else:
        morning_time = DEFAULT_MORNING
        evening_time = DEFAULT_EVENING
        weekly_time = DEFAULT_WEEKLY

    print()

    # ── Collect variables ───────────────────────────────────────────────
    user_name = ask("     Your name or handle (for AGENTS.md header)", "User") if not args.non_interactive else "User"
    user_role = ask("     Your role (e.g. 'Product Designer')", "Knowledge Worker") if not args.non_interactive else "Knowledge Worker"

    side_project_name = ""
    if features["side_project"] and not args.non_interactive:
        side_project_name = ask("     Side project name", "My Side Project")

    variables = {
        "user.name": user_name,
        "user.role": user_role,
        "user.im_channel": "DingTalk" if features["dingtalk"] else "IM",
        "user.im_assistant": "assistant",
        "user.timezone": DEFAULT_TIMEZONE,
        "user.performance_cycle": "current cycle",
        "user.side_project_name": side_project_name or "Side Project",
        "vault.path": str(vault_path),
        "config.okr_file": "05 - Reference/OKR.md",
        "config.collaborators_file": "05 - Reference/collaborators.md",
        "config.rendered_at": datetime.now().strftime("%Y-%m-%d"),
        "repo.path": str(REPO_ROOT),
        "dingtalk.scheduling_node_id": "<paste-your-node-id>",
        "dingtalk.daily_node_id": "<paste-your-node-id>",
        "cron.morning_id": "<auto-assigned>",
        "cron.morning_time": f"daily {morning_time}",
        "cron.evening_id": "<auto-assigned>",
        "cron.evening_time": f"daily {evening_time}",
        "cron.weekly_id": "<auto-assigned>",
        "cron.weekly_time": weekly_time,
        "cron.daily_doc_id": "<auto-assigned>",
        "cron.daily_doc_time": f"daily {evening_time.replace(':30', ':00').replace(':00', ':00')}",
        "cron.git_snap_id": "<auto-assigned>",
    }

    # ── Create vault ────────────────────────────────────────────────────
    print("Creating vault structure...")
    vault_path.mkdir(parents=True, exist_ok=True)
    copy_template(TEMPLATE_DIR, vault_path)

    # Create state directory
    state_dir = vault_path / ".llm-gtd"
    state_dir.mkdir(exist_ok=True)

    # ── Render AGENTS.md ────────────────────────────────────────────────
    agents_template = (TEMPLATE_DIR / "AGENTS.md").read_text(encoding="utf-8")
    rendered = render_conditionals(agents_template, features)
    rendered = render_placeholders(rendered, variables)

    agents_dest = vault_path / "AGENTS.md"
    agents_dest.write_text(rendered, encoding="utf-8")
    print(f"  ✓ AGENTS.md rendered ({len(rendered):,} chars)")

    # ── Symlink or copy knowledge base (if enabled) ─────────────────────
    if features["knowledge_base"] and KNOWLEDGE_DIR.exists():
        kb_dest = vault_path / ".llm-gtd" / "knowledge-link.txt"
        kb_dest.write_text(
            f"# GTD Knowledge Base location\n"
            f"# The AGENTS.md references pages from here.\n"
            f"path: {KNOWLEDGE_DIR / 'gtd'}\n",
            encoding="utf-8",
        )
        print(f"  ✓ Knowledge base linked at: {KNOWLEDGE_DIR / 'gtd'}")

    # ── Dashboard.app (macOS only) ───────────────────────────────────────
    import platform
    if platform.system() == "Darwin":
        try:
            from create_app import create_dashboard_app
            app_path = create_dashboard_app(str(vault_path), str(REPO_ROOT))
            print(f"  ✓ GTD Dashboard.app installed → {app_path}")
        except Exception as e:
            print(f"  ⚠ Dashboard.app skipped: {e}")

    # ── Auto-open QUICKSTART.html ──────────────────────────────────────
    quickstart = vault_path / "QUICKSTART.html"
    if quickstart.exists():
        import platform
        import subprocess
        if platform.system() == "Darwin":
            subprocess.Popen(["open", str(quickstart)])
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", str(quickstart)])
        else:
            # Windows
            os.startfile(str(quickstart))

    # ── Summary ─────────────────────────────────────────────────────────
    print()
    print("═" * 50)
    print("  Setup complete!")
    print("═" * 50)
    print()
    print(f"  Vault location:  {vault_path}")
    print(f"  AGENTS.md:       {agents_dest}")
    print(f"  Features:        {', '.join(k for k, v in features.items() if v)}")
    print()
    print("  Next steps:")
    print()
    print(f'  1. Set your environment variable:')
    print(f'     export GTD_VAULT="{vault_path}"')
    print()
    print(f'  2. Open the vault in Obsidian:')
    print(f'     Open Obsidian → "Open folder as vault" → select {vault_path}')
    print()
    print(f'  3. In QoderWork, select this vault as your working folder')
    print(f'     (the AGENTS.md will be auto-injected into every session)')
    print()
    if features["dingtalk"]:
        print(f'  4. Edit AGENTS.md §4 to paste your DingTalk document node IDs')
        print()
    print(f'  5. Register cron jobs in QoderWork:')
    print(f'     • Morning brief:  {morning_time} daily')
    print(f'     • Evening review: {evening_time} daily')
    print(f'     • Weekly review:  {weekly_time}')
    print(f'     • Git snapshot:   23:55 daily')
    print()
    print(f'  6. Run the self-check:')
    print(f'     python3 {REPO_ROOT}/setup/doctor.py --vault "{vault_path}"')
    print()
    print("  Happy GTD-ing! 🎯")
    print()


if __name__ == "__main__":
    main()
