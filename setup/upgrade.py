#!/usr/bin/env python3
"""
LLM-GTD component-aware upgrade helper.

Checks local repo / vault versions against GitHub releases and applies only the
changed managed components. User notes in 00~07 folders are always preserved.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import components as component_helpers
import init as init_helpers
from state import load_setup_state, now_iso, update_setup_state
from version import REPO_ROOT, check_for_updates, read_repo_version, read_vault_version


USER_ASSET_DIRS = {
    "00 - Inbox",
    "01 - Projects",
    "02 - Next Actions",
    "03 - Waiting For",
    "04 - Someday Maybe",
    "05 - Reference",
    "06 - Archive",
    "07 - Achievements",
}


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


def skill_upgrade_command() -> str:
    return "npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y"


def parse_component_selection(value: str | None) -> set[str] | None:
    if not value:
        return None
    return {part.strip() for part in value.split(",") if part.strip()}


def preferences(vault: Path) -> dict[str, Any]:
    state = load_setup_state(vault)
    prefs = state.get("preferences", {})
    features = {
        "okr": True,
        "doc_sync": True,
        "side_project": False,
        "knowledge_base": True,
        **prefs.get("features", {}),
    }
    im_platform = prefs.get("im_platform", "feishu")
    if im_platform == "none":
        features["doc_sync"] = False
    return {
        "im_platform": im_platform,
        "features": features,
        "morning_time": prefs.get("morning_time", init_helpers.DEFAULT_MORNING),
        "evening_time": prefs.get("evening_time", init_helpers.DEFAULT_EVENING),
        "weekly_time": prefs.get("weekly_time", init_helpers.DEFAULT_WEEKLY),
        "agent_platform": prefs.get("agent_platform", "generic"),
        "user_name": prefs.get("user_name", "User"),
        "user_role": prefs.get("user_role", "Knowledge Worker"),
        "side_project_name": prefs.get("side_project_name", "My Side Project"),
    }


def render_variables(vault: Path, repo_root: Path) -> dict[str, str]:
    prefs = preferences(vault)
    im_names = {
        "dingtalk": "DingTalk",
        "feishu": "Feishu",
        "telegram": "Telegram",
        "wecom": "WeCom",
        "wechat": "WeChat",
        "none": "IM",
    }
    return {
        "user.name": prefs["user_name"],
        "user.role": prefs["user_role"],
        "user.im_channel": im_names.get(prefs["im_platform"], "IM"),
        "user.im_assistant": "assistant",
        "user.timezone": init_helpers.DEFAULT_TIMEZONE,
        "user.performance_cycle": "current cycle",
        "user.side_project_name": prefs["side_project_name"],
        "vault.path": str(vault),
        "config.okr_file": "05 - Reference/OKR.md",
        "config.collaborators_file": "05 - Reference/collaborators.md",
        "config.rendered_at": __import__("datetime").datetime.now().strftime("%Y-%m-%d"),
        "repo.path": str(repo_root),
        "doc.scheduling_id": "<paste-your-doc-id>",
        "doc.daily_id": "<paste-your-doc-id>",
        "config.morning_time": prefs["morning_time"],
        "config.evening_time": prefs["evening_time"],
        "config.weekly_time": prefs["weekly_time"],
        "dashboard_url": f"file://{vault}/Dashboard.html",
        "doc_scheduling_url": "#",
        "doc_daily_url": "#",
    }


def backup_file(vault: Path, path: Path) -> str | None:
    if not path.exists():
        return None
    rel = path.relative_to(vault).as_posix() if path.is_relative_to(vault) else path.name
    safe_rel = rel.replace("/", "__")
    backup_dir = vault / ".llm-gtd" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{now_iso().replace(':', '').replace('+', 'Z')}__{safe_rel}"
    shutil.copy2(path, backup_path)
    return str(backup_path)


def write_managed_file(vault: Path, src: Path, dest: Path, *, backup: bool = True) -> str | None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    backup_path = backup_file(vault, dest) if backup and dest.exists() else None
    shutil.copy2(src, dest)
    return backup_path


def render_agent_instructions(vault: Path, repo_root: Path) -> dict[str, Any]:
    prefs = preferences(vault)
    template = (repo_root / "vault-template" / "AGENTS.md").read_text(encoding="utf-8")
    rendered = init_helpers.render_conditionals(template, prefs["features"])
    rendered = init_helpers.render_im_conditionals(rendered, prefs["im_platform"])
    rendered = init_helpers.render_placeholders(rendered, render_variables(vault, repo_root))

    backups = []
    for name in ("AGENTS.md", "CLAUDE.md"):
        dest = vault / name
        backup = backup_file(vault, dest)
        if backup:
            backups.append(backup)
        dest.write_text(rendered, encoding="utf-8")
    update_setup_state(
        vault,
        capabilities={"agent_instructions": "ok"},
        components={"agent_instructions": str(vault / "AGENTS.md"), "claude_md": str(vault / "CLAUDE.md")},
    )
    return {"files": ["AGENTS.md", "CLAUDE.md"], "backups": backups}


def render_quickstart(vault: Path, repo_root: Path) -> dict[str, Any]:
    prefs = preferences(vault)
    src = repo_root / "vault-template" / "QUICKSTART.html"
    text = src.read_text(encoding="utf-8")
    text = init_helpers.render_conditionals(text, prefs["features"])
    text = init_helpers.render_placeholders(text, render_variables(vault, repo_root))
    dest = vault / "QUICKSTART.html"
    backup = backup_file(vault, dest)
    dest.write_text(text, encoding="utf-8")
    update_setup_state(vault, components={"quickstart": str(dest)})
    return {"files": ["QUICKSTART.html"], "backups": [backup] if backup else []}


def update_doc_sync_protocol(vault: Path, repo_root: Path) -> dict[str, Any]:
    src = repo_root / "vault-template" / "05 - Reference" / "doc-sync-protocol.md"
    dest = vault / "05 - Reference" / "doc-sync-protocol.md"
    backup = write_managed_file(vault, src, dest)
    update_setup_state(
        vault,
        capabilities={"im_docs": "runtime_review_required"},
        components={"doc_sync_protocol": str(dest)},
    )
    return {
        "files": ["05 - Reference/doc-sync-protocol.md"],
        "backups": [backup] if backup else [],
        "runtime_action_required": "review_online_doc_sync_rules",
    }


def rewrite_agent_cron_guide(vault: Path, repo_root: Path) -> dict[str, Any]:
    from agent_cron import write_agent_cron_guide

    platform = preferences(vault)["agent_platform"]
    path = write_agent_cron_guide(vault, platform)
    update_setup_state(
        vault,
        capabilities={"agent_cron": "runtime_review_required"},
        components={"agent_cron_guide": str(path)},
    )
    return {"files": [str(path.relative_to(vault))], "runtime_action_required": "review_or_register_agent_cron"}


def update_dashboard_runtime(vault: Path, repo_root: Path) -> dict[str, Any]:
    backups = []
    for name in ("Dashboard.html", "export_dashboard.py"):
        backup = write_managed_file(vault, repo_root / "vault-template" / name, vault / name)
        if backup:
            backups.append(backup)
    export_result = subprocess.run(
        [sys.executable, str(vault / "export_dashboard.py")],
        cwd=str(vault),
        capture_output=True,
        text=True,
        timeout=30,
    )
    update_setup_state(vault, capabilities={"dashboard": "ok"}, components={"dashboard": str(vault / "Dashboard.html")})
    return {
        "files": ["Dashboard.html", "export_dashboard.py"],
        "backups": backups,
        "export_exit_code": export_result.returncode,
        "export_error": (export_result.stderr or "").strip()[:500],
    }


def copy_template_group(vault: Path, repo_root: Path, dirname: str) -> dict[str, Any]:
    src_root = repo_root / "vault-template" / dirname
    backups = []
    files = []
    for src in sorted(path for path in src_root.rglob("*") if path.is_file()):
        if src.name == ".gitkeep":
            continue
        rel = src.relative_to(src_root)
        dest = vault / dirname / rel
        backup = write_managed_file(vault, src, dest)
        if backup:
            backups.append(backup)
        files.append(f"{dirname}/{rel.as_posix()}")
    return {"files": files, "backups": backups}


def reinstall_dashboard_app(vault: Path, repo_root: Path) -> dict[str, Any]:
    if sys.platform != "darwin":
        update_setup_state(vault, capabilities={"dashboard_app": "manual_verify"})
        return {"skipped": "Dashboard.app is macOS-only"}
    from create_app import create_dashboard_app

    path = create_dashboard_app(str(vault), str(repo_root))
    update_setup_state(vault, capabilities={"dashboard_app": "ok"}, components={"dashboard_app": path})
    return {"app": path}


def reinstall_launchd(vault: Path, repo_root: Path) -> dict[str, Any]:
    if sys.platform != "darwin":
        update_setup_state(vault, capabilities={"launchd": "manual_verify", "scheduler": "manual_verify"})
        return {"skipped": "launchd is macOS-only"}
    from create_launchd import install as install_launchd

    install_launchd(str(vault))
    return {"launchd": "installed"}


def reinstall_quickcapture(vault: Path, repo_root: Path) -> dict[str, Any]:
    if sys.platform != "darwin":
        update_setup_state(vault, capabilities={"quickcapture": "skipped"})
        return {"skipped": "QuickCapture is macOS-only"}
    import install_quickcapture

    old_argv = sys.argv[:]
    try:
        sys.argv = ["install_quickcapture.py", "--vault", str(vault), "--repo", str(repo_root)]
        rc = install_quickcapture.main()
    finally:
        sys.argv = old_argv
    return {"exit_code": rc}


def recommend_skill_reinstall(vault: Path, repo_root: Path) -> dict[str, Any]:
    update_setup_state(vault, capabilities={"skill_loader": "runtime_review_required"})
    return {"runtime_action_required": skill_upgrade_command()}


def refresh_gtd_knowledge_link(vault: Path, repo_root: Path) -> dict[str, Any]:
    knowledge_path = repo_root / "knowledge" / "gtd"
    if not knowledge_path.is_dir():
        raise FileNotFoundError(f"GTD knowledge base not found: {knowledge_path}")
    dest = vault / ".llm-gtd" / "knowledge-link.txt"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        "# GTD Knowledge Base location\n"
        "# AGENTS.md references pages from here.\n"
        "# This is a repo asset, not copied user vault data.\n"
        f"path: {knowledge_path}\n",
        encoding="utf-8",
    )
    update_setup_state(
        vault,
        capabilities={"gtd_knowledge_base": "ok"},
        components={"gtd_knowledge_base": str(knowledge_path), "knowledge_link": str(dest)},
    )
    return {"files": [str(dest.relative_to(vault))], "repo_asset": str(knowledge_path)}


APPLIERS = {
    "agent_instructions": render_agent_instructions,
    "agent_cron_guide": rewrite_agent_cron_guide,
    "dashboard": update_dashboard_runtime,
    "vault_scripts": lambda vault, repo_root: copy_template_group(vault, repo_root, "Scripts"),
    "vault_templates": lambda vault, repo_root: copy_template_group(vault, repo_root, "Templates"),
    "quickstart": render_quickstart,
    "doc_sync_protocol": update_doc_sync_protocol,
    "dashboard_app": reinstall_dashboard_app,
    "launchd": reinstall_launchd,
    "quickcapture": reinstall_quickcapture,
    "gtd_knowledge_base": refresh_gtd_knowledge_link,
    "skill_loader": recommend_skill_reinstall,
}


def build_init_command(vault: Path, repo_root: Path) -> list[str]:
    """Compatibility helper retained for older tests and tooling."""
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
    if prefs.get("morning_time"):
        cmd.extend(["--morning-time", prefs["morning_time"]])
    if prefs.get("evening_time"):
        cmd.extend(["--evening-time", prefs["evening_time"]])
    if features.get("okr") is False:
        cmd.append("--disable-okr")
    if features.get("doc_sync") is False:
        cmd.append("--disable-doc-sync")
    if features.get("knowledge_base") is False:
        cmd.append("--disable-knowledge-base")
    if features.get("side_project"):
        cmd.append("--enable-side-project")
        if prefs.get("side_project_name"):
            cmd.extend(["--side-project-name", prefs["side_project_name"]])
    return cmd


def status_payload(
    vault: Path,
    repo_root: Path,
    fetch_remote: bool,
    *,
    selected_ids: set[str] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    vault_version = read_vault_version(vault)
    status = check_for_updates(
        local_repo_version=read_repo_version(),
        vault_version=vault_version,
        fetch_remote=fetch_remote,
    )
    components = component_helpers.current_component_status(
        vault,
        repo_root,
        selected_ids=selected_ids,
        force=force,
    )
    runtime_actions_required = []
    for row in components:
        if row["changed"] and row["id"] == "skill_loader":
            runtime_actions_required.append({"component": "skill_loader", "action": skill_upgrade_command()})
        if row["changed"] and row["id"] == "agent_cron_guide":
            runtime_actions_required.append({"component": "agent_cron_guide", "action": "review_or_register_agent_cron"})
        if row["changed"] and row["id"] == "doc_sync_protocol":
            runtime_actions_required.append({"component": "doc_sync_protocol", "action": "review_online_doc_sync_rules"})

    status.update({
        "vault_path": str(vault),
        "repo_path": str(repo_root),
        "skill_upgrade_command": skill_upgrade_command(),
        "components": components,
        "component_update_available": any(row["changed"] for row in components),
        "skill_reinstall_recommended": any(row["changed"] and row["id"] == "skill_loader" for row in components),
        "runtime_actions_required": runtime_actions_required,
    })
    status["update_available"] = bool(status.get("update_available") or status["component_update_available"])
    return status


def print_human_status(status: dict[str, Any]) -> None:
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   LLM-GTD Component Upgrade Check            ║")
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
    changed = [row for row in status["components"] if row["changed"]]
    if changed:
        print("  Changed components:")
        for row in changed:
            print(f"    - {row['id']} ({row['layer']}): {row['action']}")
    else:
        print("  Components look current.")
    if status.get("skill_reinstall_recommended"):
        print()
        print(f"  Skill loader changed. Reinstall only if you want the new loader: {skill_upgrade_command()}")
    print()


def apply_component(vault: Path, repo_root: Path, component: dict[str, Any], source_hash: str) -> dict[str, Any]:
    applier = APPLIERS.get(component["id"])
    if applier is None:
        raise ValueError(f"No applier for component: {component['id']}")
    result = applier(vault, repo_root)
    component_helpers.mark_component_applied(vault, component, source_hash, status="ok", details=result)
    return result


def apply_upgrade(
    vault: Path,
    repo_root: Path,
    *,
    pull_repo: bool,
    selected_ids: set[str] | None,
    force: bool,
) -> int:
    if pull_repo:
        ok, message = git_pull_repo(repo_root)
        print(f"  Git pull: {'ok' if ok else 'skipped/failed'} - {message}")

    manifest = {component["id"]: component for component in component_helpers.load_manifest(repo_root)}
    unknown = sorted(selected_ids - set(manifest)) if selected_ids else []
    if unknown:
        print(f"ERROR: Unknown component(s): {', '.join(unknown)}", file=sys.stderr)
        return 2

    rows = component_helpers.current_component_status(vault, repo_root, selected_ids=selected_ids, force=force)
    to_apply = [row for row in rows if row["changed"]]
    if not to_apply:
        print("  No changed components to apply.")
        return 0

    applied = []
    failed = []
    for row in to_apply:
        component = manifest[row["id"]]
        if component["id"] == "skill_loader":
            update_setup_state(
                vault,
                capabilities={"skill_loader": "runtime_review_required"},
                components={"skill_loader_runtime_action": skill_upgrade_command()},
            )
            print(f"  - skill_loader changed; reinstall skill separately when needed: {skill_upgrade_command()}")
            continue
        print(f"  Applying {component['id']} ({component['layer']})...")
        try:
            result = apply_component(vault, repo_root, component, row["current_hash"])
            applied.append({"id": component["id"], "result": result})
        except Exception as exc:
            failed.append({"id": component["id"], "error": str(exc)})
            component_helpers.mark_component_applied(
                vault,
                component,
                row["current_hash"],
                status="error",
                details={"error": str(exc)},
            )
            print(f"    ERROR: {exc}")

    (vault / ".llm-gtd" / "version").write_text(read_repo_version() + "\n", encoding="utf-8")
    update_setup_state(
        vault,
        components={
            "last_upgrade_at": now_iso(),
            "last_upgrade_repo_version": read_repo_version(),
            "last_component_upgrade": {"applied": applied, "failed": failed},
        },
    )
    print()
    print("  Component upgrade complete.")
    print("  User notes in 00~07 folders were preserved.")
    if failed:
        print(f"  {len(failed)} component(s) failed; inspect .llm-gtd/component-state.json.")
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check and apply LLM-GTD component upgrades")
    parser.add_argument("--vault", help="Vault path (defaults to $GTD_VAULT)")
    parser.add_argument("--repo", type=Path, default=REPO_ROOT, help="LLM-GTD repo checkout")
    parser.add_argument("--check", action="store_true", help="Check for updates only")
    parser.add_argument("--apply", action="store_true", help="Apply changed component upgrades")
    parser.add_argument("--pull-repo", action="store_true", help="Run git pull --ff-only before --apply")
    parser.add_argument("--offline", action="store_true", help="Skip GitHub release lookup")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    parser.add_argument("--components", help="Comma-separated component ids to check/apply")
    parser.add_argument("--force", action="store_true", help="Apply selected components even if hashes match")
    args = parser.parse_args()

    vault = resolve_vault(args.vault)
    repo_root = args.repo.expanduser().resolve()
    selected_ids = parse_component_selection(args.components)
    fetch_remote = not args.offline

    if args.apply:
        return apply_upgrade(
            vault,
            repo_root,
            pull_repo=args.pull_repo,
            selected_ids=selected_ids,
            force=args.force,
        )

    status = status_payload(vault, repo_root, fetch_remote, selected_ids=selected_ids, force=args.force)
    if args.json:
        print(json.dumps(status, indent=2, sort_keys=True))
    else:
        print_human_status(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
