#!/usr/bin/env python3
"""
create_launchd.py — Generate and install macOS LaunchAgent plists for LLM-GTD.

Creates two plists:
  1. com.llm-gtd.export-dashboard — runs export_dashboard.py every 30 minutes
  2. com.llm-gtd.git-snapshot — runs git add+commit at 23:55 daily

Usage:
    python3 setup/create_launchd.py --vault ~/Documents/GTD
    python3 setup/create_launchd.py --vault ~/Documents/GTD --uninstall
"""

import argparse
import plistlib
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional
from state import update_setup_state

LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
EXPECTED_LABELS = [
    "com.llm-gtd.export-dashboard",
    "com.llm-gtd.git-snapshot",
]


def labels_loaded() -> dict[str, bool]:
    try:
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {label: False for label in EXPECTED_LABELS}
    output = result.stdout
    return {label: label in output for label in EXPECTED_LABELS}


def verify_loaded() -> tuple[bool, dict[str, bool]]:
    loaded = labels_loaded()
    return all(loaded.values()), loaded


def detect_python3() -> str:
    """Pick a python3 launchd can exec.

    /usr/bin/python3 on macOS is a stub that may dispatch to Xcode CLT and can be
    missing PyYAML or even fail to invoke under launchd. Prefer the user's active
    python3 (Homebrew, asdf, pyenv, etc.). Fall back to /usr/bin/python3.
    """
    candidate = shutil.which("python3")
    if candidate:
        return candidate
    return "/usr/bin/python3"


def dumps_plist(data: dict) -> str:
    """Serialize a plist with proper XML escaping for user paths."""
    return plistlib.dumps(data, sort_keys=False).decode("utf-8")


def build_git_snapshot_command(vault: str) -> str:
    """Build a shell command that commits only when staged changes exist."""
    quoted_vault = shlex.quote(vault)
    return (
        f"cd {quoted_vault} || exit 1; "
        "if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then "
        "git init; "
        "fi; "
        "git add -A && "
        "if ! git diff --cached --quiet; then "
        "git commit -m \"auto: $(date +%Y-%m-%d_%H:%M)\"; "
        "else "
        "echo \"No changes to snapshot\"; "
        "fi"
    )


def build_export_dashboard_plist(vault: str, python3: str) -> str:
    return dumps_plist({
        "Label": "com.llm-gtd.export-dashboard",
        "ProgramArguments": [python3, f"{vault}/export_dashboard.py"],
        "WorkingDirectory": vault,
        "StartInterval": 1800,
        "StandardOutPath": f"{vault}/.llm-gtd/logs/export-dashboard.log",
        "StandardErrorPath": f"{vault}/.llm-gtd/logs/export-dashboard.err",
        "EnvironmentVariables": {"GTD_VAULT": vault},
    })


def build_git_snapshot_plist(vault: str) -> str:
    return dumps_plist({
        "Label": "com.llm-gtd.git-snapshot",
        "ProgramArguments": ["/bin/bash", "-lc", build_git_snapshot_command(vault)],
        "WorkingDirectory": vault,
        "StartCalendarInterval": {"Hour": 23, "Minute": 55},
        "StandardOutPath": f"{vault}/.llm-gtd/logs/git-snapshot.log",
        "StandardErrorPath": f"{vault}/.llm-gtd/logs/git-snapshot.err",
        "EnvironmentVariables": {"GTD_VAULT": vault},
    })

def build_plists(vault: str, python3: str) -> list[tuple[str, str]]:
    return [
        ("com.llm-gtd.export-dashboard", build_export_dashboard_plist(vault, python3)),
        ("com.llm-gtd.git-snapshot", build_git_snapshot_plist(vault)),
    ]


def install(vault_path: str):
    vault_path_obj = Path(vault_path).resolve()
    vault = str(vault_path_obj)
    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    logs_dir = Path(vault) / ".llm-gtd" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    python3 = detect_python3()
    print(f"  Using python3: {python3}")

    load_failures = []
    for label, content in build_plists(vault, python3):
        plist_path = LAUNCH_AGENTS_DIR / f"{label}.plist"
        plist_path.write_text(content, encoding="utf-8")
        print(f"  ✓ Written: {plist_path}")

        # Unload first (ignore errors if not loaded)
        subprocess.run(
            ["launchctl", "unload", str(plist_path)],
            capture_output=True
        )
        # Load
        result = subprocess.run(
            ["launchctl", "load", str(plist_path)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"    Loaded: {label}")
        else:
            print(f"    ⚠ Load failed: {result.stderr.strip()}")
            load_failures.append(label)
            update_setup_state(
                vault_path_obj,
                capabilities={"scheduler": "error", "git_snapshots": "error", "launchd": "error"},
                components={f"{label}_load_error": result.stderr.strip()},
            )

    print()
    print("  Done! Two LaunchAgents are now active:")
    print("    • export-dashboard: every 30 minutes")
    print("    • git-snapshot: daily at 23:55")
    print()
    print("  To check status: launchctl list | grep llm-gtd")
    ok, loaded = verify_loaded()
    for label, is_loaded in loaded.items():
        status = "loaded" if is_loaded else "missing"
        print(f"    • {label}: {status}")

    if load_failures or not ok:
        update_setup_state(
            vault_path_obj,
            capabilities={"scheduler": "error", "git_snapshots": "error", "launchd": "error"},
            components={"launchd": "install_failed", "launchd_loaded": loaded},
        )
        raise SystemExit(1)

    update_setup_state(
        vault_path_obj,
        capabilities={"scheduler": "ok", "git_snapshots": "ok", "launchd": "ok"},
        components={"launchd": "installed", "launchd_loaded": loaded},
    )


def uninstall(vault_path: Optional[str] = None):
    for label in ("com.llm-gtd.export-dashboard", "com.llm-gtd.git-snapshot"):
        plist_path = LAUNCH_AGENTS_DIR / f"{label}.plist"
        if plist_path.exists():
            subprocess.run(
                ["launchctl", "unload", str(plist_path)],
                capture_output=True
            )
            plist_path.unlink()
            print(f"  ✓ Removed: {label}")
        else:
            print(f"  - Not found: {label}")
    print()
    print("  LaunchAgents removed.")
    if vault_path:
        update_setup_state(
            Path(vault_path).expanduser().resolve(),
            capabilities={"scheduler": "removed", "git_snapshots": "removed", "launchd": "removed"},
            components={"launchd": "removed"},
        )


def main():
    parser = argparse.ArgumentParser(description="Install/uninstall LLM-GTD LaunchAgents")
    parser.add_argument("--vault", type=str, required=True, help="Vault path")
    parser.add_argument("--uninstall", action="store_true", help="Remove LaunchAgents")
    parser.add_argument("--verify", action="store_true", help="Verify LaunchAgents are loaded")
    args = parser.parse_args()

    if sys.platform != "darwin":
        print("ERROR: LaunchAgents are macOS-only. On Linux, use crontab.")
        print("  Add to crontab -e:")
        print(f'  */30 * * * * cd "{args.vault}" && python3 export_dashboard.py')
        cron_snapshot = build_git_snapshot_command(str(Path(args.vault).expanduser().resolve()))
        cron_snapshot = cron_snapshot.replace("%", r"\%")
        print(f"  55 23 * * * {cron_snapshot}")
        sys.exit(1)

    print()
    if args.uninstall:
        uninstall(args.vault)
    elif args.verify:
        ok, loaded = verify_loaded()
        for label, is_loaded in loaded.items():
            print(f"  {'✓' if is_loaded else '✗'} {label}")
        if not ok:
            print()
            print("  ERROR: Scheduled jobs are not loaded.")
            print(f"  Repair with: python3 setup/create_launchd.py --vault \"{args.vault}\"")
            raise SystemExit(1)
        print()
        print("  Scheduled jobs are active.")
    else:
        install(args.vault)


if __name__ == "__main__":
    main()
