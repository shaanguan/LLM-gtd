#!/usr/bin/env python3
"""
llm-gtd doctor — verify your vault setup is healthy.

Usage:
    python3 tools/setup/doctor.py [--vault PATH] [--check-cron]

Checks:
  1. $GTD_VAULT is set and directory exists
  2. Required directories present (00-Inbox through 07-Achievements)
  3. AGENTS.md exists and has no unresolved {{placeholders}}
  4. Optional tool plugin files are internally consistent when installed
  7. .llm-gtd/ state directory exists
  8. config.yaml (optional) is valid YAML if present
  9. --check-cron: verify launchd plists are loaded
"""

import os
import re
import sys
import json
from pathlib import Path
from state import update_setup_state

try:
    from agent_cron import summarize_agent_cron
except ImportError:
    summarize_agent_cron = None

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REQUIRED_DIRS = [
    "00 - Inbox",
    "01 - Projects",
    "02 - Next Actions",
    "03 - Waiting For",
    "04 - Someday Maybe",
    "05 - Reference",
    "06 - Archive",
    "07 - Achievements",
    "Templates",
]

REQUIRED_FILES = [
    "AGENTS.md",
]

DASHBOARD_PLUGIN_FILES = [
    "Dashboard.html",
    "export_dashboard.py",
]

REQUIRED_SCRIPTS = [
    "Scripts/_config.py",
    "Scripts/cron_heartbeat.py",
    "Scripts/verify_sync.py",
    "Scripts/inbox_sla.py",
    "Scripts/query_audit.py",
    "Scripts/preflight.py",
    "Scripts/dashboard_refresh_server.py",
]

KNOWLEDGE_CONTRACT_MARKERS = [
    "Knowledge & Evidence Contract",
    "Methodology is model-assisted",
    "Classify the query before answering",
    "Answer compounding",
]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_vault_path(vault: Path) -> list:
    """Verify vault exists."""
    issues = []
    if not vault.exists():
        issues.append(("FAIL", f"Vault path does not exist: {vault}"))
    elif not vault.is_dir():
        issues.append(("FAIL", f"Vault path is not a directory: {vault}"))
    return issues


def check_directories(vault: Path) -> list:
    issues = []
    for d in REQUIRED_DIRS:
        p = vault / d
        if not p.is_dir():
            issues.append(("WARN", f"Missing directory: {d}/"))
    return issues


def check_files(vault: Path) -> list:
    issues = []
    for f in REQUIRED_FILES:
        p = vault / f
        if not p.is_file():
            if f == "AGENTS.md" and (vault / "CLAUDE.md").is_file():
                issues.append(("WARN", "Missing AGENTS.md (CLAUDE.md exists — re-run init.py to add alias)"))
            else:
                issues.append(("FAIL", f"Missing file: {f}"))
    return issues


def check_dashboard_plugin(vault: Path) -> list:
    issues = []
    existing = [name for name in DASHBOARD_PLUGIN_FILES if (vault / name).is_file()]
    if not existing:
        return issues
    missing = [name for name in DASHBOARD_PLUGIN_FILES if not (vault / name).is_file()]
    for name in missing:
        issues.append(("WARN", f"Dashboard plugin partially installed; missing file: {name}"))
    return issues


def check_scripts(vault: Path) -> list:
    issues = []
    scripts_dir = vault / "Scripts"
    if not scripts_dir.exists():
        return issues
    for s in REQUIRED_SCRIPTS:
        p = vault / s
        if not p.is_file():
            issues.append(("WARN", f"Tool plugin scripts partially installed; missing script: {s}"))
    return issues


def check_claude_md(vault: Path) -> list:
    """Check AGENTS.md (or CLAUDE.md fallback) for unresolved template artifacts."""
    issues = []
    instruction_file = vault / "AGENTS.md"
    if not instruction_file.is_file():
        instruction_file = vault / "CLAUDE.md"
    if not instruction_file.is_file():
        return issues

    label = instruction_file.name
    content = instruction_file.read_text(encoding="utf-8")

    unresolved = re.findall(r'\{\{([a-z_][a-z0-9_.]*)\}\}', content)
    if unresolved:
        unique = sorted(set(unresolved))
        issues.append((
            "WARN",
            f"{label} has {len(unique)} unresolved placeholder(s): {', '.join(unique[:5])}"
            + ("..." if len(unique) > 5 else ""),
        ))

    if "<!-- IF feature." in content:
        issues.append(("WARN", f"{label} still contains <!-- IF feature. --> conditionals (not rendered?)"))
    if "<!-- IF !feature." in content:
        issues.append(("WARN", f"{label} still contains <!-- IF !feature. --> conditionals (not rendered?)"))
    if "<!-- IF im." in content:
        issues.append(("WARN", f"{label} still contains <!-- IF im. --> conditionals (IM platform not resolved)"))

    lines = content.count("\n")
    if lines > 500:
        issues.append(("INFO", f"{label} is {lines} lines — consider trimming to ≤400 for context sweet spot"))

    return issues


def instruction_file(vault: Path) -> Path | None:
    agents = vault / "AGENTS.md"
    if agents.is_file():
        return agents
    claude = vault / "CLAUDE.md"
    if claude.is_file():
        return claude
    return None


def read_knowledge_link(vault: Path) -> Path | None:
    link = vault / ".llm-gtd" / "knowledge-link.txt"
    if not link.is_file():
        return None
    for line in link.read_text(encoding="utf-8").splitlines():
        if line.startswith("path:"):
            raw = line.split(":", 1)[1].strip()
            if raw:
                return Path(raw).expanduser()
    return None


def check_knowledge_contract(vault: Path) -> list:
    issues = []
    path = instruction_file(vault)
    if path is None:
        return issues

    content = path.read_text(encoding="utf-8")
    missing = [marker for marker in KNOWLEDGE_CONTRACT_MARKERS if marker not in content]
    if missing:
        issues.append((
            "WARN",
            f"{path.name} missing knowledge/evidence contract marker(s): {', '.join(missing[:3])}"
            + ("..." if len(missing) > 3 else ""),
        ))

    if "knowledge/gtd" in content or "Knowledge & Evidence Contract" in content:
        linked = read_knowledge_link(vault)
        if linked is None:
            issues.append(("WARN", "Missing .llm-gtd/knowledge-link.txt for repo GTD knowledge base"))
        elif not linked.is_dir():
            issues.append(("WARN", f"GTD knowledge link does not point to a directory: {linked}"))

    return issues


def check_state_dir(vault: Path) -> list:
    issues = []
    state = vault / ".llm-gtd"
    if not state.is_dir():
        issues.append(("WARN", "Missing .llm-gtd/ state directory (run init.py first?)"))
    elif not (state / "logs").is_dir():
        issues.append(("WARN", "Missing .llm-gtd/logs/ directory (automation logs cannot be written)"))
    return issues


def check_version(vault: Path) -> list:
    """Check vault version against repo VERSION file."""
    issues = []
    try:
        from version import read_repo_version, read_vault_version, compare_versions
    except ImportError:
        return issues

    vault_version = read_vault_version(vault)
    repo_version = read_repo_version()
    if vault_version is None:
        issues.append(("INFO", "No .llm-gtd/version file — run tools/setup/upgrade.py --apply to stamp version"))
        return issues

    if compare_versions(vault_version, repo_version) < 0:
        issues.append((
            "WARN",
            f"Vault version {vault_version} < repo version {repo_version}. "
            f"Run: python3 tools/setup/upgrade.py --vault \"{vault}\" --apply"
        ))
    return issues


def check_remote_updates(vault: Path) -> list:
    issues = []
    try:
        from version import check_for_updates, read_vault_version, read_repo_version
    except ImportError:
        return issues

    status = check_for_updates(
        local_repo_version=read_repo_version(),
        vault_version=read_vault_version(vault),
        fetch_remote=True,
    )
    if status.get("error"):
        issues.append(("INFO", f"Could not check GitHub release: {status['error']}"))
    remote = status.get("remote_version")
    repo_version = status.get("repo_version")
    if remote and status.get("repo_behind_remote"):
        issues.append((
            "WARN",
            f"Local repo {repo_version} is behind GitHub release {remote}. "
            f"Run: git pull && python3 tools/setup/upgrade.py --vault \"{vault}\" --apply"
        ))
    if status.get("update_available"):
        issues.append((
            "INFO",
            "Upgrade skill with: npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y"
        ))
    return issues


def check_config_yaml(vault: Path) -> list:
    issues = []
    config = vault / ".llm-gtd" / "config.yaml"
    if config.is_file():
        try:
            import yaml
            with open(config, "r", encoding="utf-8") as f:
                yaml.safe_load(f)
        except ImportError:
            issues.append(("INFO", "PyYAML not installed — skipping config.yaml validation"))
        except Exception as e:
            issues.append(("FAIL", f"config.yaml is invalid YAML: {e}"))
    return issues


def check_quickcapture(vault: Path) -> list:
    """Run optional QuickCapture checks when the helper module is available."""
    try:
        from doctor_quickcapture import check as check_quickcapture_install
    except Exception as exc:
        return [("INFO", f"QuickCapture checks skipped: {exc}")]

    level_map = {"ok": "INFO", "warn": "WARN", "error": "FAIL"}
    issues = []
    for level, msg in check_quickcapture_install(str(vault)):
        mapped = level_map.get(level, "INFO")
        if mapped == "INFO" and msg.startswith("QuickCapture: skipped"):
            continue
        issues.append((mapped, msg))
    return issues


def check_env_var() -> list:
    issues = []
    val = os.environ.get("GTD_VAULT")
    if not val:
        issues.append(("INFO", "$GTD_VAULT not set in environment (optional if using --vault flag)"))
    return issues


EXPECTED_LAUNCHD_LABELS = [
    "com.llm-gtd.export-dashboard",
    "com.llm-gtd.git-snapshot",
]


def launchd_labels_loaded() -> dict[str, bool]:
    import subprocess
    try:
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True, text=True, timeout=5
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {label: False for label in EXPECTED_LAUNCHD_LABELS}
    loaded = result.stdout
    return {label: label in loaded for label in EXPECTED_LAUNCHD_LABELS}


def load_agent_platform(vault: Path) -> str:
    state_file = vault / ".llm-gtd" / "setup-state.json"
    if not state_file.is_file():
        return "generic"
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        return "generic"
    return data.get("preferences", {}).get("agent_platform", "generic")


def build_capabilities(vault: Path, include_cron: bool = False, include_quickcapture: bool = False) -> dict:
    dashboard_files = [(vault / name).is_file() for name in DASHBOARD_PLUGIN_FILES]
    dashboard_ok = all(dashboard_files)
    dashboard_partial = any(dashboard_files) and not dashboard_ok
    vault_ok = vault.is_dir() and all((vault / d).is_dir() for d in REQUIRED_DIRS)
    state_dir_ok = (vault / ".llm-gtd").is_dir()
    git_ok = (vault / ".git").is_dir()
    instructions = (vault / "AGENTS.md").is_file() or (vault / "CLAUDE.md").is_file()
    knowledge_link = read_knowledge_link(vault)

    capabilities = {
        "vault": "ok" if vault_ok else "error",
        "agent_instructions": "ok" if instructions else "missing",
        "gtd_knowledge_base": "ok" if knowledge_link and knowledge_link.is_dir() else ("missing" if knowledge_link is None else "error"),
        "dashboard": "ok" if dashboard_ok else ("warning" if dashboard_partial else "skipped"),
        "quickcapture": "unknown",
        "launchd": "unknown",
        "agent_cron": "unknown",
        "scheduler": "unknown",
        "im_docs": "unknown",
        "git_snapshots": "ok" if git_ok else "pending",
        "agent_workspace": "unknown",
        "state_dir": "ok" if state_dir_ok else "missing",
    }

    if include_cron:
        labels = launchd_labels_loaded()
        launchd_ok = all(labels.values())
        capabilities["launchd"] = "ok" if launchd_ok else "warning"
        capabilities["scheduler"] = capabilities["launchd"]
        capabilities["git_snapshots"] = "ok" if labels.get("com.llm-gtd.git-snapshot") else capabilities["git_snapshots"]
        if summarize_agent_cron:
            platform = load_agent_platform(vault)
            capabilities["agent_cron"] = summarize_agent_cron(platform)

    if include_quickcapture:
        quickcapture_bin = vault / "Scripts" / "QuickCapture.bin"
        capabilities["quickcapture"] = "ok" if quickcapture_bin.is_file() else "missing"

    claude_md = vault / "CLAUDE.md"
    agents_md = vault / "AGENTS.md"
    instruction_file = agents_md if agents_md.is_file() else claude_md
    if instruction_file.is_file():
        content = instruction_file.read_text(encoding="utf-8")
        if "<paste-your-doc-id>" in content:
            capabilities["im_docs"] = "pending"
        elif "Document sync is disabled." in content:
            capabilities["im_docs"] = "skipped"
        else:
            capabilities["im_docs"] = "configured"

    return capabilities


def check_launchd(vault: Path) -> list:
    """Check that launchd plists are loaded for local automation."""
    issues = []

    loaded = launchd_labels_loaded()
    if not any(loaded.values()) and sys.platform != "darwin":
        issues.append((
            "INFO",
            "Cannot verify launchd status (non-macOS or timeout). "
            "Manually verify export_dashboard + git snapshot jobs."
        ))
        return issues

    for label, is_loaded in loaded.items():
        if not is_loaded:
            issues.append((
                "WARN",
                f"LaunchAgent '{label}' not loaded. "
                f"Run: python3 tools/setup/create_launchd.py --vault \"{vault}\""
            ))

    return issues


def check_agent_cron(vault: Path) -> list:
    """Check whether platform agent cron jobs appear registered."""
    issues = []
    if summarize_agent_cron is None:
        return issues

    platform = load_agent_platform(vault)
    status = summarize_agent_cron(platform)
    if status == "ok":
        issues.append(("INFO", f"Agent cron jobs detected for platform '{platform}'"))
        return issues
    if status == "partial":
        issues.append(("WARN", f"Agent cron jobs only partially detected for platform '{platform}'"))
        return issues
    if status == "missing":
        issues.append((
            "WARN",
            f"Agent cron jobs missing for platform '{platform}'. "
            f"Run setup agent-cron registration from skills/llm-gtd/SKILL.md "
            f"or inspect {vault}/.llm-gtd/agent-cron-guide.md"
        ))
        return issues
    if status == "manual_verify":
        issues.append((
            "INFO",
            f"Could not auto-detect agent cron for platform '{platform}'. "
            f"Verify manually per {vault}/.llm-gtd/agent-cron-guide.md."
        ))
    return issues


def check_cron(vault: Path) -> list:
    return check_launchd(vault) + check_agent_cron(vault)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    import argparse
    parser = argparse.ArgumentParser(description="GTD Workbench Doctor — vault health check")
    parser.add_argument("--vault", type=str, help="Vault path (defaults to $GTD_VAULT)")
    parser.add_argument("--check-cron", action="store_true", help="Also verify launchd and agent cron registration")
    parser.add_argument("--check-quickcapture", action="store_true", help="Also verify QuickCapture installation")
    parser.add_argument("--json", action="store_true", help="Print machine-readable doctor results")
    parser.add_argument("--check-updates", action="store_true", help="Also check GitHub latest release")
    parser.add_argument("--fix", action="store_true", help="Auto-fix simple issues (missing dirs, state dir)")
    args = parser.parse_args()

    vault_str = args.vault or os.environ.get("GTD_VAULT")
    if not vault_str:
        print("ERROR: No vault specified. Use --vault PATH or set $GTD_VAULT")
        sys.exit(2)

    vault = Path(vault_str).expanduser().resolve()

    if not args.json:
        print()
        print("🩺 GTD Workbench Doctor")
        print(f"   Vault: {vault}")
        if args.fix:
            print("   Mode: --fix (will auto-repair where possible)")
        print("   " + "─" * 44)

    all_issues = []
    checks = [
        ("Vault path", check_vault_path),
        ("Directories", check_directories),
        ("Core files", check_files),
        ("Dashboard plugin", check_dashboard_plugin),
        ("Tool plugin scripts", check_scripts),
        ("AGENTS.md quality", check_claude_md),
        ("Knowledge contract", check_knowledge_contract),
        ("State directory", check_state_dir),
        ("Version", check_version),
        ("Config YAML", check_config_yaml),
    ]

    if args.check_cron:
        checks.append(("Launchd automation", check_launchd))
        checks.append(("Agent cron jobs", check_agent_cron))
    if args.check_quickcapture:
        checks.append(("QuickCapture", check_quickcapture))

    # Also check env var
    env_issues = check_env_var()
    if env_issues:
        all_issues.extend(env_issues)

    if args.check_updates:
        checks.append(("Remote updates", check_remote_updates))

    for name, fn in checks:
        issues = fn(vault)
        all_issues.extend(issues)

    # Print results
    fails = [i for i in all_issues if i[0] == "FAIL"]
    warns = [i for i in all_issues if i[0] == "WARN"]
    infos = [i for i in all_issues if i[0] == "INFO"]

    capabilities = build_capabilities(vault, args.check_cron, args.check_quickcapture)

    if args.json:
        payload = {
            "vault": str(vault),
            "summary": {
                "errors": len(fails),
                "warnings": len(warns),
                "infos": len(infos),
            },
            "issues": [{"level": level, "message": msg} for level, msg in all_issues],
            "capabilities": capabilities,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif not all_issues:
        print()
        print("   ✅ All checks passed! Your vault is healthy.")
    else:
        print()
        for level, msg in all_issues:
            icon = {"FAIL": "❌", "WARN": "⚠️ ", "INFO": "ℹ️ "}[level]
            print(f"   {icon} [{level}] {msg}")

    if not args.json:
        print()
        print(f"   Summary: {len(fails)} error(s), {len(warns)} warning(s), {len(infos)} info(s)")

    # --fix: auto-repair simple issues
    if args.fix and (warns or fails):
        if not args.json:
            print()
            print("   🔧 Auto-fix results:")
        fixed = 0
        for level, msg in all_issues:
            if "Missing directory:" in msg:
                dirname = msg.split("Missing directory: ")[1].rstrip("/")
                (vault / dirname).mkdir(parents=True, exist_ok=True)
                if not args.json:
                    print(f"      ✓ Created {dirname}/")
                fixed += 1
            elif "Missing .llm-gtd/ state directory" in msg:
                (vault / ".llm-gtd" / "logs").mkdir(parents=True, exist_ok=True)
                if not args.json:
                    print(f"      ✓ Created .llm-gtd/ and .llm-gtd/logs/")
                fixed += 1
            elif "Missing .llm-gtd/logs/ directory" in msg:
                (vault / ".llm-gtd" / "logs").mkdir(parents=True, exist_ok=True)
                if not args.json:
                    print(f"      ✓ Created .llm-gtd/logs/")
                fixed += 1
        if not args.json:
            if fixed:
                print(f"      Fixed {fixed} issue(s).")
            else:
                print(f"      No auto-fixable issues found (remaining issues need manual intervention).")

    update_setup_state(
        vault,
        steps={"verify": "ok" if not fails else "error"},
        capabilities=capabilities,
        components={"doctor_last_summary": {"errors": len(fails), "warnings": len(warns), "infos": len(infos)}},
    )

    if not args.json:
        print()

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
