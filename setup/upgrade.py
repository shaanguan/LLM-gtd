#!/usr/bin/env python3
"""
LLM-GTD upgrade helper.

Checks local repo / vault versions against GitHub releases and applies vault
runtime upgrades without touching user notes in 00~07 folders.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from state import load_setup_state, update_setup_state
from version import REPO_ROOT, check_for_updates, read_repo_version, read_vault_version


def resolve_vault(explicit: str | None) -> Path:
    raw = explicit or os.environ.get("GTD_VAULT")
    if not raw:
        print("ERROR: Use --vault PATH or set $GTD_VAULT", file=sys.stderr)
        sys.exit(2)
    vault = Path(raw).expanduser().resolve()
    if not vault.is_dir():
        print(f"ERROR: Vault not found: {vault}", file=sys.stderr)
        sys.exit(2)
    return vault


def git_pull_repo(repo_root: Path) -> tuple[bool, str]:
    if not (repo_root / ".git").is_dir():
        return False, "Repo is not a git checkout; pull skipped"
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "pull", "--ff-only"],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "git pull failed").strip()
        return False, message
    return True, (result.stdout or "git pull ok").strip()


def build_init_command(vault: Path, repo_root: Path) -> list[str]:
    prefs = load_setup_state(vault).get("preferences", {})
    features = prefs.get("features", {})
    cmd = [
        sys.executable,
        str(repo_root / "setup" / "init.py"),
        "--vault",
        str(vault),
        "--non-interactive",
        "--agent-platform",
        prefs.get("agent_platform", "generic"),
        "--no-open",
    ]
    im_platform = prefs.get("im_platform")
    if im_platform:
        cmd.extend(["--im-platform", im_platform])
    morning = prefs.get("morning_time")
    evening = prefs.get("evening_time")
    if morning:
        cmd.extend(["--morning-time", morning])
    if evening:
        cmd.extend(["--evening-time", evening])
    if features.get("okr") is False:
        cmd.append("--disable-okr")
    if features.get("doc_sync") is False:
        cmd.append("--disable-doc-sync")
    if features.get("knowledge_base") is False:
        cmd.append("--disable-knowledge-base")
    if features.get("side_project"):
        cmd.append("--enable-side-project")
        side_name = prefs.get("side_project_name")
        if side_name:
            cmd.extend(["--side-project-name", side_name])
    return cmd


def run_init_upgrade(vault: Path, repo_root: Path) -> int:
    cmd = build_init_command(vault, repo_root)
    print("  Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    return result.returncode


def verify_launchd(vault: Path, repo_root: Path) -> int:
    cmd = [
        sys.executable,
        str(repo_root / "setup" / "create_launchd.py"),
        "--vault",
        str(vault),
        "--verify",
    ]
    return subprocess.run(cmd).returncode


def skill_upgrade_command() -> str:
    return "npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y"


def status_payload(vault: Path, repo_root: Path, fetch_remote: bool) -> dict:
    vault_version = read_vault_version(vault)
    status = check_for_updates(
        local_repo_version=read_repo_version(),
        vault_version=vault_version,
        fetch_remote=fetch_remote,
    )
    status["vault_path"] = str(vault)
    status["repo_path"] = str(repo_root)
    status["skill_upgrade_command"] = skill_upgrade_command()
    return status


def print_human_status(status: dict) -> None:
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   LLM-GTD Upgrade Check                      ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    print(f"  Vault:          {status['vault_path']}")
    print(f"  Repo:           {status['repo_path']}")
    print(f"  Repo version:   {status['repo_version']}")
    print(f"  Vault version:  {status.get('vault_version') or 'missing'}")
    print(f"  Remote release: {status.get('remote_version') or 'unknown'}")
    if status.get("error"):
        print(f"  Remote check:   {status['error']}")
    print()
    if status.get("update_available"):
        print("  ⚠ Update available.")
        if status.get("vault_behind_repo"):
            print("    - Vault runtime files are older than this repo checkout.")
        if status.get("repo_behind_remote"):
            print("    - Local repo checkout is older than GitHub latest release.")
        print()
        print("  Recommended:")
        print(f"    1) Upgrade skill:  {status['skill_upgrade_command']}")
        print(f"    2) Apply vault:    python3 setup/upgrade.py --vault \"{status['vault_path']}\" --apply")
    else:
        print("  ✓ Vault and repo look current against the latest known release.")
    print()


def apply_upgrade(vault: Path, repo_root: Path, *, pull_repo: bool) -> int:
    if pull_repo:
        ok, message = git_pull_repo(repo_root)
        print(f"  Git pull: {'ok' if ok else 'skipped/failed'} — {message}")

    rc = run_init_upgrade(vault, repo_root)
    if rc != 0:
        print(f"ERROR: init upgrade failed with exit code {rc}", file=sys.stderr)
        return rc

    import platform

    if platform.system() == "Darwin":
        verify_launchd(vault, repo_root)

    update_setup_state(
        vault,
        components={
            "last_upgrade_at": __import__("state").now_iso(),
            "last_upgrade_repo_version": read_repo_version(),
        },
    )

    print()
    print("  Upgrade applied to vault runtime files.")
    print("  User notes in 00~07 folders were preserved.")
    print(f"  Also run: {skill_upgrade_command()}")
    print()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check and apply LLM-GTD upgrades")
    parser.add_argument("--vault", help="Vault path (defaults to $GTD_VAULT)")
    parser.add_argument("--repo", type=Path, default=REPO_ROOT, help="LLM-GTD repo checkout")
    parser.add_argument("--check", action="store_true", help="Check for updates only")
    parser.add_argument("--apply", action="store_true", help="Apply vault runtime upgrade")
    parser.add_argument("--pull-repo", action="store_true", help="Run git pull --ff-only before --apply")
    parser.add_argument("--offline", action="store_true", help="Skip GitHub release lookup")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    args = parser.parse_args()

    vault = resolve_vault(args.vault)
    repo_root = args.repo.expanduser().resolve()
    fetch_remote = not args.offline

    if args.apply:
        return apply_upgrade(vault, repo_root, pull_repo=args.pull_repo)

    status = status_payload(vault, repo_root, fetch_remote)
    if args.json:
        print(json.dumps(status, indent=2, sort_keys=True))
    else:
        print_human_status(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
