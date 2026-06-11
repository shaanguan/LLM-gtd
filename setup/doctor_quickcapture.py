#!/usr/bin/env python3
"""
doctor_quickcapture.py — Health checks for QuickCapture installation.

Returns a list of (level, message) tuples:
  level: "ok", "warn", "error"
"""

import subprocess
import platform
from pathlib import Path
from typing import List, Tuple


def check(vault_path: str) -> List[Tuple[str, str]]:
    """Run QuickCapture health checks. Returns list of (level, message)."""
    results = []

    if platform.system() != "Darwin":
        results.append(("ok", "QuickCapture: skipped (not macOS)"))
        return results

    vault = Path(vault_path).expanduser().resolve()

    # 1. Check binary exists
    bin_path = vault / "Scripts" / "QuickCapture.bin"
    jxa_path = vault / "Scripts" / "QuickCapture.jxa"

    if bin_path.exists():
        results.append(("ok", f"QuickCapture binary: {bin_path}"))
    elif jxa_path.exists():
        results.append(("ok", f"QuickCapture JXA fallback: {jxa_path}"))
    else:
        results.append(("warn", "QuickCapture not installed (no .bin or .jxa in Scripts/)"))
        return results

    # 2. Check LaunchAgent plist exists
    plist = Path.home() / "Library" / "LaunchAgents" / "com.gtd.quickcapture.plist"
    if plist.exists():
        results.append(("ok", f"LaunchAgent plist: {plist}"))
    else:
        results.append(("error", "LaunchAgent plist missing: ~/Library/LaunchAgents/com.gtd.quickcapture.plist"))
        return results

    # 3. Check if loaded
    try:
        proc = subprocess.run(
            ["launchctl", "list"],
            capture_output=True, text=True, timeout=5
        )
        if "com.gtd.quickcapture" in proc.stdout:
            results.append(("ok", "LaunchAgent is loaded and running"))
        else:
            results.append(("warn", "LaunchAgent plist exists but not loaded (run: launchctl load -w ~/Library/LaunchAgents/com.gtd.quickcapture.plist)"))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        results.append(("warn", "Could not check launchctl status"))

    # 4. Check Accessibility (best-effort, not always detectable)
    # We can't programmatically check this without calling AXIsProcessTrusted from Swift/ObjC.
    # Just remind the user.
    results.append(("ok", "Accessibility permission: cannot verify programmatically — ensure QuickCapture.bin is checked in System Settings > Privacy & Security > Accessibility"))

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 doctor_quickcapture.py /path/to/vault")
        sys.exit(1)
    for level, msg in check(sys.argv[1]):
        icon = {"ok": "\u2705", "warn": "\u26a0\ufe0f", "error": "\u274c"}[level]
        print(f"  {icon} {msg}")
