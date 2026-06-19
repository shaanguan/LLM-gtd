#!/usr/bin/env python3
"""
install_quickcapture.py — Build and install QuickCapture for macOS.

Usage:
    python3 install_quickcapture.py --vault /path/to/vault --repo /path/to/llm-gtd

This script:
1. Checks for Swift toolchain (xcrun --find swift) — required
2. Builds the Swift package
3. Copies binary to $VAULT/Scripts/
4. Renders & installs LaunchAgent plist
5. Loads the LaunchAgent
"""

import os
import sys
import shutil
import subprocess
import platform
import plistlib
from pathlib import Path
from typing import Optional
from xml.sax.saxutils import escape
from state import update_setup_state


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
    pkg_dir = repo_path / "tools" / "scripts" / "quickcapture"
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


def render_launchagent_plist(template: str, bin_path: Path, inbox_dir: Path) -> str:
    """Render the LaunchAgent template and validate it as plist XML."""
    rendered = template.replace("__QUICKCAPTURE_BIN__", escape(str(bin_path)))
    rendered = rendered.replace("__INBOX_DIR__", escape(str(inbox_dir)))
    plistlib.loads(rendered.encode("utf-8"))
    return rendered


def install_launchagent(bin_path: Path, repo_path: Path, inbox_dir: Path) -> bool:
    """Render plist template and load LaunchAgent."""
    template = repo_path / "tools" / "scripts" / "quickcapture" / "com.gtd.quickcapture.plist.template"
    if not template.exists():
        print("  [!] plist template not found")
        return False

    try:
        plist_content = render_launchagent_plist(template.read_text(encoding="utf-8"), bin_path, inbox_dir)
    except Exception as exc:
        print(f"  [!] plist template is invalid: {exc}")
        return False

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


def check_legacy_automator_services():
    """Detect legacy Automator .workflow files that may conflict with Cmd+I."""
    services_dir = Path.home() / "Library" / "Services"
    if not services_dir.exists():
        return

    conflicts = []
    for wf in services_dir.glob("*.workflow"):
        name_lower = wf.stem.lower()
        if "gtd" in name_lower and "capture" in name_lower:
            conflicts.append(wf)

    if not conflicts:
        return

    print()
    print("  ⚠️  Legacy Automator service(s) detected that may conflict with ⌘I:")
    for wf in conflicts:
        print(f"     • {wf}")
    print()
    print("  These use macOS 'display dialog' and will shadow the new QuickCapture panel.")
    print("  To fix: System Settings → Keyboard → Keyboard Shortcuts → Services")
    print("          → uncheck or remove the conflicting shortcut.")
    print(f"  Or delete: mv \"{conflicts[0]}\" ~/.Trash/")
    print()


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

    # Check for legacy Automator services that conflict with hotkeys
    check_legacy_automator_services()

    if not has_swift():
        print("  [!] Swift toolchain not found.")
        print("  QuickCapture requires Xcode Command Line Tools. Install with:")
        print("      xcode-select --install")
        print("  Then re-run setup. Skipping QuickCapture for now.")
        update_setup_state(vault_path, capabilities={"quickcapture": "missing_toolchain"})
        return 0

    binary = build_swift(repo_path)
    if not binary:
        print("  [!] Swift build failed. Skipping QuickCapture install.")
        update_setup_state(vault_path, capabilities={"quickcapture": "error"}, components={"quickcapture": "build failed"})
        return 1

    dest = install_binary(binary, vault_path)
    inbox_dir = vault_path / "00 - Inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    loaded = install_launchagent(dest, repo_path, inbox_dir)
    update_setup_state(
        vault_path,
        capabilities={"quickcapture": "ok" if loaded else "partial"},
        components={"quickcapture_bin": str(dest), "quickcapture_launchagent": "loaded" if loaded else "load_failed"},
    )
    print("\n  ** First time you press Cmd+I, macOS will ask for Accessibility permission.")
    print("  ** Go to: System Settings > Privacy & Security > Accessibility")
    print("  ** Check the box next to QuickCapture.bin\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
