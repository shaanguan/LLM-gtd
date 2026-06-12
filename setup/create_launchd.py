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
import os
import shutil
import subprocess
import sys
from pathlib import Path

LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"


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


PLIST_EXPORT_DASHBOARD = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.llm-gtd.export-dashboard</string>
  <key>ProgramArguments</key>
  <array>
    <string>{python3}</string>
    <string>{vault}/export_dashboard.py</string>
  </array>
  <key>WorkingDirectory</key>
  <string>{vault}</string>
  <key>StartInterval</key>
  <integer>1800</integer>
  <key>StandardOutPath</key>
  <string>{vault}/.llm-gtd/logs/export-dashboard.log</string>
  <key>StandardErrorPath</key>
  <string>{vault}/.llm-gtd/logs/export-dashboard.err</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>GTD_VAULT</key>
    <string>{vault}</string>
  </dict>
</dict>
</plist>
"""

PLIST_GIT_SNAPSHOT = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.llm-gtd.git-snapshot</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>cd "{vault}" &amp;&amp; git add -A &amp;&amp; git diff --cached --quiet || git commit -m "auto: $(date +%Y-%m-%d_%H:%M)"</string>
  </array>
  <key>WorkingDirectory</key>
  <string>{vault}</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>23</integer>
    <key>Minute</key>
    <integer>55</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>{vault}/.llm-gtd/logs/git-snapshot.log</string>
  <key>StandardErrorPath</key>
  <string>{vault}/.llm-gtd/logs/git-snapshot.err</string>
</dict>
</plist>
"""

PLISTS = [
    ("com.llm-gtd.export-dashboard", PLIST_EXPORT_DASHBOARD),
    ("com.llm-gtd.git-snapshot", PLIST_GIT_SNAPSHOT),
]


def install(vault_path: str):
    vault = str(Path(vault_path).resolve())
    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    logs_dir = Path(vault) / ".llm-gtd" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    python3 = detect_python3()
    print(f"  Using python3: {python3}")

    for label, template in PLISTS:
        content = template.format(vault=vault, python3=python3)
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

    print()
    print("  Done! Two LaunchAgents are now active:")
    print("    • export-dashboard: every 30 minutes")
    print("    • git-snapshot: daily at 23:55")
    print()
    print("  To check status: launchctl list | grep llm-gtd")


def uninstall():
    for label, _ in PLISTS:
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


def main():
    parser = argparse.ArgumentParser(description="Install/uninstall LLM-GTD LaunchAgents")
    parser.add_argument("--vault", type=str, required=True, help="Vault path")
    parser.add_argument("--uninstall", action="store_true", help="Remove LaunchAgents")
    args = parser.parse_args()

    if sys.platform != "darwin":
        print("ERROR: LaunchAgents are macOS-only. On Linux, use crontab.")
        print("  Add to crontab -e:")
        print(f'  */30 * * * * cd "{args.vault}" && python3 export_dashboard.py')
        print(f'  55 23 * * * cd "{args.vault}" && git add -A && git diff --cached --quiet || git commit -m "auto: $(date +\\%Y-\\%m-\\%d)"')
        sys.exit(1)

    print()
    if args.uninstall:
        uninstall()
    else:
        install(args.vault)


if __name__ == "__main__":
    main()
