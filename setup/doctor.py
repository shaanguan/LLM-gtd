#!/usr/bin/env python3
"""
llm-gtd doctor — verify your vault setup is healthy.

Usage:
    python3 setup/doctor.py [--vault PATH] [--check-cron]

Checks:
  1. $GTD_VAULT is set and directory exists
  2. Required directories present (00-Inbox through 07-Achievements)
  3. CLAUDE.md exists and has no unresolved {{placeholders}}
  4. Scripts/ present and importable
  5. Dashboard.html exists
  6. export_dashboard.py exists
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
    "Scripts",
    "Templates",
]

REQUIRED_FILES = [
    "CLAUDE.md",
    "Dashboard.html",
    "export_dashboard.py",
]

REQUIRED_SCRIPTS = [
    "Scripts/_config.py",
    "Scripts/cron_heartbeat.py",
    "Scripts/verify_sync.py",
    "Scripts/inbox_sla.py",
    "Scripts/preflight.py",
    "Scripts/dashboard_refresh_server.py",
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
            issues.append(("FAIL", f"Missing file: {f}"))
    return issues


def check_scripts(vault: Path) -> list:
    issues = []
    for s in REQUIRED_SCRIPTS:
        p = vault / s
        if not p.is_file():
            issues.append(("WARN", f"Missing script: {s}"))
    return issues


def check_claude_md(vault: Path) -> list:
    issues = []
    claude_md = vault / "CLAUDE.md"
    if not claude_md.is_file():
        return issues  # already caught by check_files

    content = claude_md.read_text(encoding="utf-8")

    # Check for unresolved placeholders
    unresolved = re.findall(r'\{\{([a-z_][a-z0-9_.]*)\}\}', content)
    if unresolved:
        unique = sorted(set(unresolved))
        issues.append((
            "WARN",
            f"CLAUDE.md has {len(unique)} unresolved placeholder(s): {', '.join(unique[:5])}"
            + ("..." if len(unique) > 5 else ""),
        ))

    # Check for unprocessed conditionals
    if "<!-- IF feature." in content:
        issues.append(("WARN", "CLAUDE.md still contains <!-- IF feature. --> conditionals (not rendered?)"))
    if "<!-- IF !feature." in content:
        issues.append(("WARN", "CLAUDE.md still contains <!-- IF !feature. --> conditionals (not rendered?)"))
    if "<!-- IF im." in content:
        issues.append(("WARN", "CLAUDE.md still contains <!-- IF im. --> conditionals (IM platform not resolved)"))

    # Basic size check
    lines = content.count("\n")
    if lines > 500:
        issues.append(("INFO", f"CLAUDE.md is {lines} lines — consider trimming to ≤400 for context sweet spot"))

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
    """Check vault version against repo version for upgrade detection."""
    issues = []
    version_file = vault / ".llm-gtd" / "version"
    if not version_file.is_file():
        issues.append(("INFO", "No .llm-gtd/version file — cannot detect upgrades (pre-1.1.0 vault?)"))
        return issues

    # Import VERSION from init.py or fallback
    repo_root = Path(__file__).resolve().parent.parent
    init_py = repo_root / "setup" / "init.py"
    repo_version = "unknown"
    if init_py.is_file():
        for line in init_py.read_text(encoding="utf-8").splitlines():
            if line.startswith("VERSION"):
                repo_version = line.split('"')[1] if '"' in line else line.split("'")[1]
                break

    vault_version = version_file.read_text(encoding="utf-8").strip()
    if vault_version != repo_version and repo_version != "unknown":
        issues.append((
            "WARN",
            f"Vault version {vault_version} < repo version {repo_version}. "
            f"Run: python3 setup/init.py --vault \"{vault}\" to upgrade runtime files."
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


def build_capabilities(vault: Path, include_cron: bool = False, include_quickcapture: bool = False) -> dict:
    dashboard_ok = (vault / "Dashboard.html").is_file() and (vault / "export_dashboard.py").is_file()
    vault_ok = vault.is_dir() and all((vault / d).is_dir() for d in REQUIRED_DIRS)
    state_dir_ok = (vault / ".llm-gtd").is_dir()
    git_ok = (vault / ".git").is_dir()

    capabilities = {
        "vault": "ok" if vault_ok else "error",
        "dashboard": "ok" if dashboard_ok else "error",
        "quickcapture": "unknown",
        "scheduler": "unknown",
        "im_docs": "unknown",
        "git_snapshots": "ok" if git_ok else "pending",
        "agent_workspace": "unknown",
        "state_dir": "ok" if state_dir_ok else "missing",
    }

    if include_cron:
        labels = launchd_labels_loaded()
        scheduler_ok = all(labels.values())
        capabilities["scheduler"] = "ok" if scheduler_ok else "warning"
        capabilities["git_snapshots"] = "ok" if labels.get("com.llm-gtd.git-snapshot") else capabilities["git_snapshots"]

    if include_quickcapture:
        quickcapture_bin = vault / "Scripts" / "QuickCapture.bin"
        capabilities["quickcapture"] = "ok" if quickcapture_bin.is_file() else "missing"

    claude_md = vault / "CLAUDE.md"
    if claude_md.is_file():
        content = claude_md.read_text(encoding="utf-8")
        if "<paste-your-doc-id>" in content:
            capabilities["im_docs"] = "pending"
        elif "Document sync is disabled." in content:
            capabilities["im_docs"] = "skipped"
        else:
            capabilities["im_docs"] = "configured"

    return capabilities


def check_cron(vault: Path) -> list:
    """Check that launchd plists are loaded for automated tasks."""
    issues = []

    loaded = launchd_labels_loaded()
    if not any(loaded.values()) and sys.platform != "darwin":
        issues.append((
            "INFO",
            "Cannot verify launchd status (non-macOS or timeout). "
            "Manually verify your scheduler is running export_dashboard + git snapshot."
        ))
        return issues

    for label, is_loaded in loaded.items():
        if not is_loaded:
            issues.append((
                "WARN",
                f"LaunchAgent '{label}' not loaded. "
                f"Run: python3 setup/create_launchd.py --vault \"{vault}\""
            ))

    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    import argparse
    parser = argparse.ArgumentParser(description="GTD Workbench Doctor — vault health check")
    parser.add_argument("--vault", type=str, help="Vault path (defaults to $GTD_VAULT)")
    parser.add_argument("--check-cron", action="store_true", help="Also verify cron task registration")
    parser.add_argument("--check-quickcapture", action="store_true", help="Also verify QuickCapture installation")
    parser.add_argument("--json", action="store_true", help="Print machine-readable doctor results")
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
        ("Scripts", check_scripts),
        ("CLAUDE.md quality", check_claude_md),
        ("State directory", check_state_dir),
        ("Version", check_version),
        ("Config YAML", check_config_yaml),
    ]

    if args.check_cron:
        checks.append(("Cron tasks", check_cron))
    if args.check_quickcapture:
        checks.append(("QuickCapture", check_quickcapture))

    # Also check env var
    env_issues = check_env_var()
    if env_issues:
        all_issues.extend(env_issues)

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
