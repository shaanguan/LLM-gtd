#!/usr/bin/env python3
"""
llm-gtd interactive initializer.

Usage:
    python3 setup/init.py [--vault PATH]

Walks you through setup questions, renders vault-template/ into your vault,
installs local automation, opens QUICKSTART, and prints next-step guidance.
Targets any AGENTS.md/CLAUDE.md-compatible agent, with OpenClaw/Hermes first.
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from state import load_setup_state, update_setup_state

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

FEATURES_ALL = ["okr", "doc_sync", "side_project", "knowledge_base"]

IM_PLATFORMS = ["feishu", "dingtalk", "telegram", "wecom", "wechat"]

# Version written to .llm-gtd/version for upgrade detection
VERSION = "1.1.0"

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


def validate_hhmm(value: str, label: str) -> str:
    """Validate a 24-hour HH:MM time string."""
    if not re.fullmatch(r"\d{2}:\d{2}", value):
        raise ValueError(f"{label} must use HH:MM format, got: {value}")
    hour, minute = (int(part) for part in value.split(":"))
    if hour > 23 or minute > 59:
        raise ValueError(f"{label} must be a valid 24-hour time, got: {value}")
    return value


def render_conditionals(text: str, features: dict) -> str:
    """
    Process <!-- IF feature.X --> and <!-- IF !feature.X --> blocks.
    """
    # Pattern: <!-- IF !?feature.xxx --> ... (<!-- ELSE --> ...)? <!-- ENDIF -->
    pattern = re.compile(
        r'<!-- IF (!?)feature\.(\w+) -->\s*\n(.*?)(?:<!-- ELSE -->\s*\n(.*?))?<!-- ENDIF -->\s*\n',
        re.DOTALL,
    )

    def replacer(m):
        negated = bool(m.group(1))
        feat = m.group(2)
        if_block = m.group(3)
        else_block = m.group(4) or ""
        enabled = features.get(feat, False)
        if enabled != negated:
            return if_block
        else:
            return else_block

    return pattern.sub(replacer, text)


def render_im_conditionals(text: str, im_platform: str) -> str:
    """
    Process <!-- IF im.xxx --> ... <!-- /IF --> blocks.
    Keeps the block matching the chosen IM platform, removes all others.
    """
    pattern = re.compile(
        r'<!-- IF im\.(\w+) -->\s*\n(.*?)<!-- /IF -->\s*\n',
        re.DOTALL,
    )

    def replacer(m):
        platform = m.group(1)
        block = m.group(2)
        if platform == im_platform:
            return block
        else:
            return ""

    return pattern.sub(replacer, text)


def render_placeholders(text: str, variables: dict) -> str:
    """Replace {{key.subkey}} placeholders with values from a flat dict."""
    def replacer(m):
        key = m.group(1)
        return variables.get(key, m.group(0))  # keep unresolved as-is

    return re.compile(r'\{\{([a-z_][a-z0-9_.]*)\}\}').sub(replacer, text)


def copy_template(template_dir: Path, dest: Path, skip_agents: bool = True):
    """
    Recursively copy vault-template/ to dest, skipping CLAUDE.md
    (which gets rendered separately) and .gitkeep files.
    """
    for src_path in sorted(template_dir.rglob("*")):
        rel = src_path.relative_to(template_dir)

        # Skip CLAUDE.md — we render it with variables
        if skip_agents and rel.name == "CLAUDE.md":
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


def status_label(value: str) -> str:
    labels = {
        "ok": "OK",
        "skipped": "SKIPPED",
        "pending": "PENDING",
        "partial": "PARTIAL",
        "unknown": "UNKNOWN",
        "error": "ERROR",
        "missing": "MISSING",
        "missing_toolchain": "MISSING TOOLCHAIN",
    }
    return labels.get(value, str(value).upper())


def write_setup_report(vault_path: Path) -> Path:
    """Write a human-readable setup report for the user and agent."""
    state = load_setup_state(vault_path)
    capabilities = state.get("capabilities", {})
    steps = state.get("steps", {})
    report = vault_path / ".llm-gtd" / "setup-report.md"
    lines = [
        "# LLM-GTD Setup Report",
        "",
        f"Updated: {state.get('updated_at', '')}",
        f"Vault: `{vault_path}`",
        f"Next step: `{state.get('next_step', 'unknown')}`",
        "",
        "## Capabilities",
        "",
    ]
    for key in ["vault", "dashboard", "scheduler", "git_snapshots", "quickcapture", "im_docs", "agent_workspace"]:
        lines.append(f"- **{key}**: {status_label(capabilities.get(key, 'unknown'))}")
    lines.extend(["", "## Setup Steps", ""])
    for key in ["detect_repo", "ask_preferences", "init_vault", "install_local_tools", "connect_im_docs", "verify", "onboard"]:
        lines.append(f"- **{key}**: {status_label(steps.get(key, 'pending'))}")
    lines.extend([
        "",
        "## How to verify automation",
        "",
        "- macOS launchd labels: `com.llm-gtd.export-dashboard`, `com.llm-gtd.git-snapshot`",
        "- Check from terminal: `launchctl list | grep llm-gtd`",
        "- Machine-readable check: `python3 setup/doctor.py --vault \"$GTD_VAULT\" --check-cron --check-quickcapture --json`",
        "",
    ])
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Initialize a GTD Workbench vault")
    parser.add_argument("--vault", type=str, help="Target vault path (skip interactive question)")
    parser.add_argument("--non-interactive", action="store_true", help="Use all defaults")
    parser.add_argument("--no-open", action="store_true", help="Do not open QUICKSTART.html after setup")
    parser.add_argument("--no-app", action="store_true", help="Do not create Dashboard.app on macOS")
    parser.add_argument("--skip-automation", action="store_true", help="Do not install launchd automation")
    parser.add_argument("--skip-quickcapture", action="store_true", help="Do not install QuickCapture")
    parser.add_argument("--user-name", default="User", help="Name or handle for CLAUDE.md")
    parser.add_argument("--user-role", default="Knowledge Worker", help="Role for CLAUDE.md")
    parser.add_argument("--im-platform", choices=IM_PLATFORMS + ["none"], help="Document sync IM platform")
    parser.add_argument("--disable-okr", action="store_true", help="Disable OKR tracking")
    parser.add_argument("--disable-doc-sync", action="store_true", help="Disable document sync")
    parser.add_argument("--enable-side-project", action="store_true", help="Enable side-project tracking")
    parser.add_argument("--side-project-name", default="My Side Project", help="Side-project name")
    parser.add_argument("--disable-knowledge-base", action="store_true", help="Disable GTD knowledge references")
    parser.add_argument("--morning-time", default=DEFAULT_MORNING, help="Morning brief time, HH:MM")
    parser.add_argument("--evening-time", default=DEFAULT_EVENING, help="Evening review time, HH:MM")
    parser.add_argument("--weekly-time", default=DEFAULT_WEEKLY, help="Weekly review time, e.g. 'Sun 21:00'")
    args = parser.parse_args()

    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   GTD Workbench — Interactive Setup          ║")
    print("║   Your AI GTD secretary                      ║")
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
        "okr": not args.disable_okr,
        "doc_sync": not args.disable_doc_sync,
        "side_project": args.enable_side_project,
        "knowledge_base": not args.disable_knowledge_base,
    }
    im_platform = args.im_platform or "feishu"  # default

    if not args.non_interactive:
        features["okr"] = ask_yn("2/3  Enable OKR tracking? (links NAs to objectives)", True)
        features["doc_sync"] = ask_yn("     Enable document sync (shared scheduling/daily doc)?", True)
        if features["doc_sync"]:
            print("     IM platform for document sync:")
            print("       1) Feishu  2) DingTalk  3) Telegram  4) WeCom  5) WeChat")
            im_choice = ask("     Choose [1-5]", "1")
            im_platform = {"1": "feishu", "2": "dingtalk", "3": "telegram", "4": "wecom", "5": "wechat"}.get(im_choice, "feishu")
        else:
            im_platform = "none"
        features["side_project"] = ask_yn("     Track a personal side project (separate from work)?", False)
        features["knowledge_base"] = ask_yn("     Include GTD knowledge base references?", True)
        print()
    elif not features["doc_sync"]:
        im_platform = "none"

    if im_platform == "none":
        features["doc_sync"] = False

    # ── Question 3: Routine preferences ─────────────────────────────────
    if not args.non_interactive:
        morning_time = ask("3/3  Preferred morning brief time (HH:MM)", DEFAULT_MORNING)
        evening_time = ask("     Preferred evening review time (HH:MM)", DEFAULT_EVENING)
        weekly_time = ask("     Preferred weekly review (e.g. 'Sun 21:00')", DEFAULT_WEEKLY)
    else:
        morning_time = args.morning_time
        evening_time = args.evening_time
        weekly_time = args.weekly_time

    try:
        morning_time = validate_hhmm(morning_time, "morning time")
        evening_time = validate_hhmm(evening_time, "evening time")
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

    print()

    # ── Collect variables ───────────────────────────────────────────────
    user_name = ask("     Your name or handle (for CLAUDE.md header)", args.user_name) if not args.non_interactive else args.user_name
    user_role = ask("     Your role (e.g. 'Product Designer')", args.user_role) if not args.non_interactive else args.user_role

    side_project_name = ""
    if features["side_project"] and not args.non_interactive:
        side_project_name = ask("     Side project name", args.side_project_name)
    elif features["side_project"]:
        side_project_name = args.side_project_name

    im_names = {"dingtalk": "DingTalk", "feishu": "Feishu", "telegram": "Telegram", "wecom": "WeCom", "wechat": "WeChat", "none": "IM"}
    variables = {
        "user.name": user_name,
        "user.role": user_role,
        "user.im_channel": im_names.get(im_platform, "IM"),
        "user.im_assistant": "assistant",
        "user.timezone": DEFAULT_TIMEZONE,
        "user.performance_cycle": "current cycle",
        "user.side_project_name": side_project_name or "Side Project",
        "vault.path": str(vault_path),
        "config.okr_file": "05 - Reference/OKR.md",
        "config.collaborators_file": "05 - Reference/collaborators.md",
        "config.rendered_at": datetime.now().strftime("%Y-%m-%d"),
        "repo.path": str(REPO_ROOT),
        "doc.scheduling_id": "<paste-your-doc-id>",
        "doc.daily_id": "<paste-your-doc-id>",
        "config.morning_time": morning_time,
        "config.evening_time": evening_time,
        "config.weekly_time": weekly_time,
        # QUICKSTART links
        "dashboard_url": f"file://{vault_path}/Dashboard.html",
        "doc_scheduling_url": "#",
        "doc_daily_url": "#",
    }

    # ── Create vault ────────────────────────────────────────────────────
    print("Creating vault structure...")
    vault_path.mkdir(parents=True, exist_ok=True)
    copy_template(TEMPLATE_DIR, vault_path)

    # Create state directory
    state_dir = vault_path / ".llm-gtd"
    state_dir.mkdir(exist_ok=True)
    (state_dir / "logs").mkdir(exist_ok=True)

    # Write version for upgrade detection (#6)
    (state_dir / "version").write_text(VERSION + "\n", encoding="utf-8")
    update_setup_state(
        vault_path,
        steps={
            "detect_repo": "ok",
            "ask_preferences": "ok",
            "init_vault": "in_progress",
        },
        capabilities={"vault": "ok"},
        preferences={
            "im_platform": im_platform,
            "features": features,
            "morning_time": morning_time,
            "evening_time": evening_time,
            "weekly_time": weekly_time,
        },
        components={"repo_path": str(REPO_ROOT), "version": VERSION},
    )

    # ── Render CLAUDE.md ───────────────────────────────────────────────
    agents_template = (TEMPLATE_DIR / "CLAUDE.md").read_text(encoding="utf-8")
    rendered = render_conditionals(agents_template, features)
    rendered = render_im_conditionals(rendered, im_platform)
    rendered = render_placeholders(rendered, variables)

    agents_dest = vault_path / "CLAUDE.md"
    agents_dest.write_text(rendered, encoding="utf-8")
    print(f"  ✓ CLAUDE.md rendered ({len(rendered):,} chars)")
    update_setup_state(vault_path, components={"agent_instructions": str(agents_dest)})

    # ── Render QUICKSTART.html ──────────────────────────────────────────
    quickstart_src = vault_path / "QUICKSTART.html"
    if quickstart_src.exists():
        qs_text = quickstart_src.read_text(encoding="utf-8")
        qs_text = render_conditionals(qs_text, features)
        qs_text = render_placeholders(qs_text, variables)
        quickstart_src.write_text(qs_text, encoding="utf-8")
        print(f"  ✓ QUICKSTART.html rendered")
        update_setup_state(vault_path, components={"quickstart": str(quickstart_src)})

    # ── Symlink or copy knowledge base (if enabled) ─────────────────────
    if features["knowledge_base"] and KNOWLEDGE_DIR.exists():
        kb_dest = vault_path / ".llm-gtd" / "knowledge-link.txt"
        kb_dest.write_text(
            f"# GTD Knowledge Base location\n"
            f"# The CLAUDE.md references pages from here.\n"
            f"path: {KNOWLEDGE_DIR / 'gtd'}\n",
            encoding="utf-8",
        )
        print(f"  ✓ Knowledge base linked at: {KNOWLEDGE_DIR / 'gtd'}")
    update_setup_state(
        vault_path,
        steps={"init_vault": "ok"},
        capabilities={"dashboard": "ok"},
        components={"dashboard": str(vault_path / "Dashboard.html")},
    )

    # ── Dashboard.app (macOS only) ───────────────────────────────────────
    import platform
    if platform.system() == "Darwin" and not args.no_app:
        try:
            from create_app import create_dashboard_app
            app_path = create_dashboard_app(str(vault_path), str(REPO_ROOT))
            print(f"  ✓ GTD Dashboard.app installed → {app_path}")
            update_setup_state(vault_path, components={"dashboard_app": app_path})
        except Exception as e:
            print(f"  ⚠ Dashboard.app skipped: {e}")
            update_setup_state(vault_path, components={"dashboard_app": f"skipped: {e}"})

    # ── One-click local automation (macOS only) ─────────────────────────
    if platform.system() == "Darwin" and not args.skip_automation:
        try:
            from create_launchd import install as install_launchd
            install_launchd(str(vault_path))
            print("  ✓ launchd automation installed")
            update_setup_state(vault_path, capabilities={"scheduler": "ok", "git_snapshots": "ok"})
        except Exception as e:
            print(f"  ⚠ launchd automation skipped: {e}")
            update_setup_state(vault_path, capabilities={"scheduler": "error", "git_snapshots": "error"}, components={"launchd_error": str(e)})
    elif args.skip_automation:
        update_setup_state(vault_path, capabilities={"scheduler": "skipped", "git_snapshots": "skipped"})

    if platform.system() == "Darwin" and not args.skip_quickcapture:
        try:
            import install_quickcapture
            old_argv = sys.argv[:]
            sys.argv = [
                "install_quickcapture.py",
                "--vault",
                str(vault_path),
                "--repo",
                str(REPO_ROOT),
            ]
            rc = install_quickcapture.main()
            sys.argv = old_argv
            if rc == 0:
                print("  ✓ QuickCapture installed or skipped gracefully")
                update_setup_state(vault_path, capabilities={"quickcapture": "ok"})
            else:
                print(f"  ⚠ QuickCapture installer exited with code {rc}")
                update_setup_state(vault_path, capabilities={"quickcapture": "error"}, components={"quickcapture_exit_code": rc})
        except Exception as e:
            sys.argv = old_argv if "old_argv" in locals() else sys.argv
            print(f"  ⚠ QuickCapture skipped: {e}")
            update_setup_state(vault_path, capabilities={"quickcapture": "error"}, components={"quickcapture_error": str(e)})
    elif args.skip_quickcapture:
        update_setup_state(vault_path, capabilities={"quickcapture": "skipped"})

    update_setup_state(
        vault_path,
        steps={
            "install_local_tools": "ok" if (platform.system() != "Darwin" or not (args.skip_automation or args.skip_quickcapture)) else "skipped",
            "connect_im_docs": "pending" if features["doc_sync"] else "skipped",
            "onboard": "pending",
        },
        capabilities={"im_docs": "pending" if features["doc_sync"] else "skipped"},
    )
    setup_report = write_setup_report(vault_path)
    update_setup_state(vault_path, components={"setup_report": str(setup_report)})

    # ── Auto-open QUICKSTART.html ──────────────────────────────────────
    quickstart = vault_path / "QUICKSTART.html"
    if quickstart.exists() and not args.no_open:
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
    print(f"  CLAUDE.md:       {agents_dest}")
    print(f"  Features:        {', '.join(k for k, v in features.items() if v)}")
    print(f"  Setup report:    {setup_report}")
    print()
    state = load_setup_state(vault_path)
    capabilities = state.get("capabilities", {})
    print("  Installed components:")
    print(f"    Dashboard:      {status_label(capabilities.get('dashboard', 'unknown'))}")
    print(f"    Scheduler:      {status_label(capabilities.get('scheduler', 'unknown'))}")
    print(f"    Git snapshots:  {status_label(capabilities.get('git_snapshots', 'unknown'))}")
    print(f"    QuickCapture:   {status_label(capabilities.get('quickcapture', 'unknown'))}")
    print(f"    Online docs:    {status_label(capabilities.get('im_docs', 'unknown'))}")
    print()
    print("  Next steps:")
    print()
    step = 1
    print(f'  {step}. Set your environment variable (add to ~/.zshrc):')
    print(f'     export GTD_VAULT="{vault_path}"')
    print()
    step += 1
    print(f'  {step}. Open the vault in Obsidian:')
    print(f'     Open Obsidian → "Open folder as vault" → select {vault_path}')
    print()
    step += 1
    print(f'  {step}. Add the vault to your agent workspace:')
    print(f'     OpenClaw / Hermes / Claude Desktop / Cursor → add folder → select {vault_path}')
    print(f'     (CLAUDE.md will be read automatically by compatible agents)')
    print()
    if features["doc_sync"]:
        step += 1
        print(f'  {step}. Create or connect your {im_names[im_platform]} online docs')
        print(f'     The setup skill should create docs via MCP when credentials are available;')
        print(f'     otherwise paste the document IDs into CLAUDE.md §4.')
        print()
    if args.skip_automation:
        step += 1
        print(f'  {step}. Install launchd plists for automation:')
        print(f'     python3 {REPO_ROOT}/setup/create_launchd.py --vault "{vault_path}"')
        print(f'     (creates: export_dashboard every 30min + git snapshot at 23:55)')
        print()
    if args.skip_quickcapture:
        step += 1
        print(f'  {step}. Install QuickCapture:')
        print(f'     python3 {REPO_ROOT}/setup/install_quickcapture.py --vault "{vault_path}" --repo "{REPO_ROOT}"')
        print()
    step += 1
    print(f'  {step}. Run the self-check:')
    print(f'     python3 {REPO_ROOT}/setup/doctor.py --vault "{vault_path}"')
    print()
    print("  Happy GTD-ing! 🎯")
    print()


if __name__ == "__main__":
    main()
