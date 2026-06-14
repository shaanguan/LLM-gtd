#!/usr/bin/env python3
"""
Safe LLM-GTD uninstall.

Removes automation and optional system files only. User vault content in
00 - Inbox through 07 - Achievements is always preserved.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional

from state import update_setup_state

LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"

USER_ASSET_DIRS = [
    "00 - Inbox",
    "01 - Projects",
    "02 - Next Actions",
    "03 - Waiting For",
    "04 - Someday Maybe",
    "05 - Reference",
    "06 - Archive",
    "07 - Achievements",
]

SYSTEM_LAUNCH_AGENT_LABELS = [
    "com.llm-gtd.export-dashboard",
    "com.llm-gtd.git-snapshot",
    "com.gtd.quickcapture",
]


def remove_launch_agent(label: str) -> bool:
    plist_path = LAUNCH_AGENTS_DIR / f"{label}.plist"
    if not plist_path.exists():
        print(f"  - Not found: {label}")
        return False

    subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
    plist_path.unlink()
    print(f"  ✓ Removed LaunchAgent: {label}")
    return True


def count_user_notes(vault: Path) -> int:
    total = 0
    for dirname in USER_ASSET_DIRS:
        folder = vault / dirname
        if folder.is_dir():
            total += sum(1 for path in folder.rglob("*.md") if path.is_file())
    return total


def uninstall(
    vault_path: str,
    purge_state: bool = False,
    remove_dashboard_app: bool = False,
) -> int:
    vault = Path(vault_path).expanduser().resolve()
    if not vault.is_dir():
        print(f"ERROR: Vault path does not exist: {vault}")
        return 2

    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   LLM-GTD Safe Uninstall                     ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    print(f"  Vault: {vault}")
    print(f"  User notes preserved in 00~07: {count_user_notes(vault)} markdown file(s)")
    print()

    print("  Removing scriptable computer tools only:")
    removed = 0
    for label in SYSTEM_LAUNCH_AGENT_LABELS:
        if remove_launch_agent(label):
            removed += 1

    if purge_state:
        state_dir = vault / ".llm-gtd"
        if state_dir.is_dir():
            for child in sorted(state_dir.iterdir(), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    for nested in sorted(child.rglob("*"), reverse=True):
                        if nested.is_file():
                            nested.unlink()
                    child.rmdir()
            state_dir.rmdir()
            print("  ✓ Removed .llm-gtd/ setup state")
    else:
        print("  - Kept .llm-gtd/ setup state (use --purge-state to remove)")

    if remove_dashboard_app:
        app_path = Path.home() / "Applications" / "GTD Dashboard.app"
        if app_path.exists():
            import shutil
            shutil.rmtree(app_path)
            print(f"  ✓ Removed {app_path}")
        else:
            print("  - Dashboard.app not found in ~/Applications")

    print()
    print("  Preserved user assets (never deleted):")
    for dirname in USER_ASSET_DIRS:
        marker = "✓" if (vault / dirname).exists() else "-"
        print(f"    {marker} {dirname}/")
    print()
    print("  Your tasks, projects, archive, and achievements remain in the vault.")
    print("  This script cannot remove platform agent cron jobs, IM gateways,")
    print("  online document credentials, or the installed skill package.")
    print("  Runtime cleanup is still required if those were configured.")
    print("    See `.llm-gtd/agent-cron-guide.md` and setup-state.json.")
    print()

    update_setup_state(
        vault,
        capabilities={
            "agent_cron": "runtime_cleanup_pending",
            "im_docs": "runtime_cleanup_pending",
            "skill_loader": "manual_removal_required",
            "launchd": "removed",
            "scheduler": "removed",
            "git_snapshots": "removed",
            "quickcapture": "removed",
        },
        components={
            "uninstall": "computer_tools_removed",
            "runtime_cleanup": "pending",
        },
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely uninstall LLM-GTD automation")
    parser.add_argument("--vault", required=True, help="Vault path")
    parser.add_argument("--purge-state", action="store_true", help="Also remove .llm-gtd/ state")
    parser.add_argument("--remove-dashboard-app", action="store_true", help="Also remove ~/Applications/GTD Dashboard.app")
    args = parser.parse_args()

    if sys.platform != "darwin":
        print("NOTE: LaunchAgents are macOS-only. On other platforms, remove your cron jobs manually.")
    return uninstall(args.vault, args.purge_state, args.remove_dashboard_app)


if __name__ == "__main__":
    raise SystemExit(main())
