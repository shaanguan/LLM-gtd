#!/usr/bin/env python3
"""Generate a macOS .app bundle that opens Dashboard.html in Chrome."""

import os
import shutil
import stat
import sys

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
open -a "Google Chrome" "file://{dashboard_path}"
"""


def create_dashboard_app(vault_path: str, repo_path: str, install_dir: str = None):
    """Create GTD Dashboard.app pointing to vault's Dashboard.html.

    Args:
        vault_path: Absolute path to the user's vault.
        repo_path: Absolute path to the llm-gtd repo (for icon resources).
        install_dir: Where to place the .app. Defaults to ~/Applications.
    """
    if install_dir is None:
        install_dir = os.path.expanduser("~/Applications")

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
    with open(launch_path, "w") as f:
        f.write(LAUNCH_TEMPLATE.format(dashboard_path=dashboard_html))
    os.chmod(launch_path, os.stat(launch_path).st_mode | stat.S_IXUSR | stat.S_IXGRP)

    # Icons
    icons_src = os.path.join(repo_path, "resources")
    for icon in ("AppIcon.icns", "AppIcon.png"):
        src = os.path.join(icons_src, icon)
        if os.path.exists(src):
            shutil.copy2(src, res_dir)

    return app_dir


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: create_app.py <vault_path> <repo_path> [install_dir]")
        sys.exit(1)
    vault = sys.argv[1]
    repo = sys.argv[2]
    dest = sys.argv[3] if len(sys.argv) > 3 else None
    result = create_dashboard_app(vault, repo, dest)
    print(f"Created: {result}")
