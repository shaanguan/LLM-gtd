#!/usr/bin/env python3
"""
install_quickcapture.py — Build and install QuickCapture for macOS.

Usage:
    python3 install_quickcapture.py --vault /path/to/vault --repo /path/to/llm-gtd

This script:
1. Checks for Swift toolchain (xcrun --find swift)
2. Builds the Swift package (or falls back to JXA)
3. Copies binary/script to $VAULT/Scripts/
4. Renders & installs LaunchAgent plist
5. Loads the LaunchAgent
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Optional


def is_macos():
    return platform.system() == "Darwin"


def has_swift():
    """Check if Swift toolchain is available."""
    try:
        result = subprocess.run(
            ["xcrun", "--find", "swift"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def build_swift(repo_path: Path) -> Optional[Path]:
    """Build QuickCapture Swift package. Returns binary path or None."""
    pkg_dir = repo_path / "scripts" / "quickcapture"
    if not (pkg_dir / "Package.swift").exists():
        print("  [!] Package.swift not found")
        return None

    print("  Building QuickCapture (swift build -c release)...")
    result = subprocess.run(
        ["swift", "build", "-c", "release"],
        cwd=str(pkg_dir),
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"  [!] Build failed:\n{result.stderr[:500]}")
        return None

    binary = pkg_dir / ".build" / "release" / "QuickCapture"
    if binary.exists():
        print("  Build successful.")
        return binary
    return None


def install_binary(binary_path: Path, vault_path: Path) -> Path:
    """Copy binary to vault Scripts directory."""
    dest_dir = vault_path / "Scripts"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "QuickCapture.bin"
    shutil.copy2(str(binary_path), str(dest))
    os.chmod(str(dest), 0o755)
    print(f"  Installed: {dest}")
    return dest


def install_jxa_fallback(repo_path: Path, vault_path: Path) -> Path:
    """Copy JXA script as fallback."""
    src = repo_path / "scripts" / "quickcapture" / "QuickCapture.jxa"
    dest_dir = vault_path / "Scripts"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "QuickCapture.jxa"

    # Replace __INBOX_DIR__ placeholder
    inbox_dir = str(vault_path / "00 - Inbox")
    content = src.read_text(encoding="utf-8")
    content = content.replace("__INBOX_DIR__", inbox_dir)
    dest.write_text(content, encoding="utf-8")
    os.chmod(str(dest), 0o755)
    print(f"  Installed JXA fallback: {dest}")
    return dest


def install_launchagent(bin_path: Path, repo_path: Path) -> bool:
    """Render plist template and load LaunchAgent."""
    template = repo_path / "scripts" / "quickcapture" / "com.gtd.quickcapture.plist.template"
    if not template.exists():
        print("  [!] plist template not found")
        return False

    plist_content = template.read_text(encoding="utf-8")
    plist_content = plist_content.replace("__QUICKCAPTURE_BIN__", str(bin_path))

    la_dir = Path.home() / "Library" / "LaunchAgents"
    la_dir.mkdir(parents=True, exist_ok=True)
    plist_dest = la_dir / "com.gtd.quickcapture.plist"

    # Unload existing if present
    if plist_dest.exists():
        subprocess.run(
            ["launchctl", "unload", str(plist_dest)],
            capture_output=True, timeout=10
        )

    plist_dest.write_text(plist_content, encoding="utf-8")
    print(f"  LaunchAgent: {plist_dest}")

    # Load
    result = subprocess.run(
        ["launchctl", "load", "-w", str(plist_dest)],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0:
        print("  LaunchAgent loaded successfully.")
        return True
    else:
        print(f"  [!] launchctl load failed: {result.stderr}")
        return False


def patch_inbox_dir_in_swift(repo_path: Path, vault_path: Path):
    """Replace __INBOX_DIR__ in main.swift before building."""
    main_swift = repo_path / "scripts" / "quickcapture" / "Sources" / "QuickCapture" / "main.swift"
    if not main_swift.exists():
        return
    inbox_dir = str(vault_path / "00 - Inbox")
    content = main_swift.read_text(encoding="utf-8")
    if "__INBOX_DIR__" in content:
        content = content.replace("__INBOX_DIR__", inbox_dir)
        main_swift.write_text(content, encoding="utf-8")


def main():
    if not is_macos():
        print("QuickCapture is macOS-only. Skipping.")
        return 0

    import argparse
    parser = argparse.ArgumentParser(description="Install QuickCapture")
    parser.add_argument("--vault", required=True, help="Vault path")
    parser.add_argument("--repo", required=True, help="LLM-GTD repo path")
    args = parser.parse_args()

    vault_path = Path(args.vault).expanduser().resolve()
    repo_path = Path(args.repo).expanduser().resolve()

    print("\n[QuickCapture Install]")

    if has_swift():
        # Patch inbox dir before building
        patch_inbox_dir_in_swift(repo_path, vault_path)
        binary = build_swift(repo_path)
        if binary:
            dest = install_binary(binary, vault_path)
            install_launchagent(dest, repo_path)
            print("\n  ** First time you press Cmd+I, macOS will ask for Accessibility permission.")
            print("  ** Go to: System Settings > Privacy & Security > Accessibility")
            print("  ** Check the box next to QuickCapture.bin\n")
            return 0

    # Fallback to JXA
    print("  Swift not available, using JXA fallback...")
    jxa_dest = install_jxa_fallback(repo_path, vault_path)

    # For JXA, the LaunchAgent runs osascript
    # Create a wrapper plist manually
    la_dir = Path.home() / "Library" / "LaunchAgents"
    la_dir.mkdir(parents=True, exist_ok=True)
    plist_dest = la_dir / "com.gtd.quickcapture.plist"

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
\t<key>Label</key>
\t<string>com.gtd.quickcapture</string>
\t<key>ProgramArguments</key>
\t<array>
\t\t<string>/usr/bin/osascript</string>
\t\t<string>-l</string>
\t\t<string>JavaScript</string>
\t\t<string>{jxa_dest}</string>
\t</array>
\t<key>RunAtLoad</key>
\t<true/>
\t<key>KeepAlive</key>
\t<true/>
\t<key>StandardOutPath</key>
\t<string>/dev/null</string>
\t<key>StandardErrorPath</key>
\t<string>/dev/null</string>
</dict>
</plist>"""

    if plist_dest.exists():
        subprocess.run(["launchctl", "unload", str(plist_dest)], capture_output=True, timeout=10)
    plist_dest.write_text(plist_content, encoding="utf-8")
    subprocess.run(["launchctl", "load", "-w", str(plist_dest)], capture_output=True, timeout=10)

    print(f"  LaunchAgent installed (JXA mode).")
    print("\n  Note: JXA version uses file-based toggle (touch /tmp/gtd-toggle).")
    print("  Create a Shortcut or Automator service with a hotkey to trigger it.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
