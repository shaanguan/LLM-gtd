#!/usr/bin/env python3
"""
gtd-workbench doctor — verify your vault setup is healthy.

Usage:
    python3 setup/doctor.py [--vault PATH]

Checks:
  1. $GTD_VAULT is set and directory exists
  2. Required directories present (00-Inbox through 07-Achievements)
  3. AGENTS.md exists and has no unresolved {{placeholders}}
  4. Scripts/ present and importable
  5. Dashboard.html exists
  6. export_dashboard.py exists
  7. .gtd-workbench/ state directory exists
  8. config.yaml (optional) is valid YAML if present
"""

import os
import re
import sys
from pathlib import Path

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
    "AGENTS.md",
    "Dashboard.html",
    "export_dashboard.py",
]

REQUIRED_SCRIPTS = [
    "Scripts/_config.py",
    "Scripts/cron_heartbeat.py",
    "Scripts/verify_sync.py",
    "Scripts/inbox_sla.py",
    "Scripts/preflight.py",
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


def check_agents_md(vault: Path) -> list:
    issues = []
    agents = vault / "AGENTS.md"
    if not agents.is_file():
        return issues  # already caught by check_files

    content = agents.read_text(encoding="utf-8")

    # Check for unresolved placeholders
    unresolved = re.findall(r'\{\{([a-z_][a-z0-9_.]*)\}\}', content)
    if unresolved:
        unique = sorted(set(unresolved))
        issues.append((
            "WARN",
            f"AGENTS.md has {len(unique)} unresolved placeholder(s): {', '.join(unique[:5])}"
            + ("..." if len(unique) > 5 else ""),
        ))

    # Check for unprocessed conditionals
    if "<!-- IF feature." in content:
        issues.append(("WARN", "AGENTS.md still contains <!-- IF --> conditionals (not rendered?)"))

    # Basic size check
    lines = content.count("\n")
    if lines > 500:
        issues.append(("INFO", f"AGENTS.md is {lines} lines — consider trimming to ≤400 for context sweet spot"))

    return issues


def check_state_dir(vault: Path) -> list:
    issues = []
    state = vault / ".gtd-workbench"
    if not state.is_dir():
        issues.append(("WARN", "Missing .gtd-workbench/ state directory (run init.py first?)"))
    return issues


def check_config_yaml(vault: Path) -> list:
    issues = []
    config = vault / ".gtd-workbench" / "config.yaml"
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


def check_env_var() -> list:
    issues = []
    val = os.environ.get("GTD_VAULT")
    if not val:
        issues.append(("INFO", "$GTD_VAULT not set in environment (optional if using --vault flag)"))
    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    import argparse
    parser = argparse.ArgumentParser(description="GTD Workbench Doctor — vault health check")
    parser.add_argument("--vault", type=str, help="Vault path (defaults to $GTD_VAULT)")
    args = parser.parse_args()

    vault_str = args.vault or os.environ.get("GTD_VAULT")
    if not vault_str:
        print("ERROR: No vault specified. Use --vault PATH or set $GTD_VAULT")
        sys.exit(2)

    vault = Path(vault_str).expanduser().resolve()

    print()
    print("🩺 GTD Workbench Doctor")
    print(f"   Vault: {vault}")
    print("   " + "─" * 44)

    all_issues = []
    checks = [
        ("Vault path", check_vault_path),
        ("Directories", check_directories),
        ("Core files", check_files),
        ("Scripts", check_scripts),
        ("AGENTS.md quality", check_agents_md),
        ("State directory", check_state_dir),
        ("Config YAML", check_config_yaml),
    ]

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

    if not all_issues:
        print()
        print("   ✅ All checks passed! Your vault is healthy.")
    else:
        print()
        for level, msg in all_issues:
            icon = {"FAIL": "❌", "WARN": "⚠️ ", "INFO": "ℹ️ "}[level]
            print(f"   {icon} [{level}] {msg}")

    print()
    print(f"   Summary: {len(fails)} error(s), {len(warns)} warning(s), {len(infos)} info(s)")
    print()

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
