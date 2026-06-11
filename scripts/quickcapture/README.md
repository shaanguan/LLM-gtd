# QuickCapture

A lightweight macOS-only global hotkey tool that lets you instantly capture thoughts into your GTD Inbox from anywhere.

**Platform**: macOS 13+ only. Linux/Windows users should skip this component.

## How it works

Press **Cmd+I** anywhere on your Mac to summon a floating HUD panel. Type your thought, press Enter — it becomes a timestamped markdown file in `00 - Inbox/`.

- **Enter** — save and close
- **Shift+Enter** — newline (multi-line capture)
- **Cmd+I** again — hide (saves draft, restored next time)
- **Esc** — discard and close

## Installation (automated)

If you ran `setup/init.py`, QuickCapture was automatically compiled and installed. The setup script:

1. Compiles the Swift package (`swift build -c release`)
2. Copies the binary to `$GTD_VAULT/Scripts/QuickCapture.bin`
3. Installs a LaunchAgent so it starts automatically at login
4. Reminds you to grant Accessibility permission

## Manual installation

```bash
cd scripts/quickcapture
swift build -c release
cp .build/release/QuickCapture "$GTD_VAULT/Scripts/QuickCapture.bin"
```

Then install the LaunchAgent:

```bash
# Replace placeholder with your actual binary path
sed "s|__QUICKCAPTURE_BIN__|$GTD_VAULT/Scripts/QuickCapture.bin|g" \
    com.gtd.quickcapture.plist.template > ~/Library/LaunchAgents/com.gtd.quickcapture.plist

launchctl load -w ~/Library/LaunchAgents/com.gtd.quickcapture.plist
```

## Accessibility permission

The first time you press Cmd+I, macOS will prompt you to grant Accessibility access:

**System Settings > Privacy & Security > Accessibility** — check the box next to `QuickCapture.bin` (or `QuickCapture` if shown by name).

Without this permission, the global hotkey will not work.

## Uninstallation

```bash
launchctl unload ~/Library/LaunchAgents/com.gtd.quickcapture.plist
rm ~/Library/LaunchAgents/com.gtd.quickcapture.plist
rm "$GTD_VAULT/Scripts/QuickCapture.bin"
```

## JXA fallback

If you don't have the Swift toolchain (Xcode / Command Line Tools), the setup script installs `QuickCapture.jxa` instead. This version uses a file-based toggle (`touch /tmp/gtd-toggle`) rather than a native global hotkey.

To trigger it, create a Shortcut (Shortcuts.app) or Automator service that runs:
```bash
touch /tmp/gtd-toggle
```
Then assign your preferred keyboard shortcut to that Shortcut.

## Changing the hotkey

The default is **Cmd+I** (`kVK_ANSI_I` = keyCode 34). If this conflicts with apps you use (Sketch, Figma, etc.), edit `Sources/QuickCapture/main.swift`:

```swift
// In registerGlobalHotKey():
RegisterEventHotKey(
    UInt32(kVK_ANSI_I),   // ← Change this (e.g., kVK_ANSI_Period for Cmd+.)
    UInt32(cmdKey),        // ← Or change modifiers (cmdKey | shiftKey for Cmd+Shift)
    ...
)
```

Then rebuild:
```bash
cd scripts/quickcapture && swift build -c release
cp .build/release/QuickCapture "$GTD_VAULT/Scripts/QuickCapture.bin"
# Restart the daemon:
launchctl kickstart -k gui/$(id -u)/com.gtd.quickcapture
```

Common key codes: `kVK_ANSI_Period` (0x2F), `kVK_ANSI_Slash` (0x2C), `kVK_Space` (0x31).
