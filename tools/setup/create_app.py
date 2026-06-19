#!/usr/bin/env python3
"""Generate a macOS .app bundle that opens Dashboard.html in Chrome."""

import os
import shutil
import stat
import sys
from pathlib import Path
import argparse

PLIST_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>launch</string>
  <key>CFBundleName</key>
  <string>GTD Dashboard</string>
  <key>CFBundleIdentifier</key>
  <string>com.llm-gtd.dashboard</string>
  <key>CFBundleVersion</key>
  <string>1.0</string>
  <key>CFBundleIconFile</key>
  <string>AppIcon</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
</dict>
</plist>
"""

LAUNCH_TEMPLATE = """\
#!/bin/bash
export GTD_VAULT="{vault_path}"
if ! /usr/bin/curl -fsS "http://127.0.0.1:8765/health" >/dev/null 2>&1; then
  /usr/bin/nohup /usr/bin/python3 "{refresh_server_path}" >/tmp/llm-gtd-dashboard-refresh.log 2>&1 &
  sleep 0.4
fi
open -a "Google Chrome" "file://{dashboard_path}"
"""


def create_dashboard_app(vault_path: str, repo_path: str = None, install_dir: str = None):
    """Create GTD Dashboard.app pointing to vault's Dashboard.html.

    Args:
        vault_path: Absolute path to the user's vault.
        repo_path: Absolute path to the llm-gtd repo (for icon resources).
            Defaults to the parent directory of this script.
        install_dir: Where to place the .app. Defaults to ~/Applications.
    """
    if install_dir is None:
        install_dir = os.path.expanduser("~/Applications")
    if repo_path is None:
        repo_path = str(Path(__file__).resolve().parent.parent.parent)

    dashboard_html = os.path.join(vault_path, "Dashboard.html")
    app_dir = os.path.join(install_dir, "GTD Dashboard.app")
    macos_dir = os.path.join(app_dir, "Contents", "MacOS")
    res_dir = os.path.join(app_dir, "Contents", "Resources")

    # Clean previous install
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)

    os.makedirs(macos_dir)
    os.makedirs(res_dir)

    # Info.plist
    with open(os.path.join(app_dir, "Contents", "Info.plist"), "w") as f:
        f.write(PLIST_TEMPLATE)

    # Launch script
    launch_path = os.path.join(macos_dir, "launch")
    refresh_server_path = os.path.join(vault_path, "Scripts", "dashboard_refresh_server.py")
    with open(launch_path, "w") as f:
        f.write(
            LAUNCH_TEMPLATE.format(
                vault_path=vault_path,
                dashboard_path=dashboard_html,
                refresh_server_path=refresh_server_path,
            )
        )
    os.chmod(launch_path, os.stat(launch_path).st_mode | stat.S_IXUSR | stat.S_IXGRP)

    # Icons
    icons_src = os.path.join(repo_path, "tools", "resources")
    for icon in ("AppIcon.icns", "AppIcon.png"):
        src = os.path.join(icons_src, icon)
        if os.path.exists(src):
            shutil.copy2(src, res_dir)

    return app_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create GTD Dashboard.app")
    parser.add_argument("vault_path", help="Path to the GTD vault")
    parser.add_argument("repo_path", nargs="?", help="Path to the LLM-GTD repo")
    parser.add_argument("install_dir", nargs="?", help="Directory where the .app should be installed")
    args = parser.parse_args()

    result = create_dashboard_app(args.vault_path, args.repo_path, args.install_dir)
    print(f"Created: {result}")
