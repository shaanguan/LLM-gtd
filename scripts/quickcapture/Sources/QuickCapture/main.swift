import Cocoa

// MARK: - Configuration
// __INBOX_DIR__ is replaced by install_quickcapture.py at install time.
// If running from source without replacement, defaults to ~/Documents/GTD/00 - Inbox
let vaultPath: URL = {
    let placeholder = "__INBOX_DIR__"
    if placeholder.hasPrefix("__") {
        return FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Documents/GTD/00 - Inbox")
    }
    return URL(fileURLWithPath: placeholder)
}()

// MARK: - TextField Delegate
class CaptureFieldDelegate: NSObject, NSTextFieldDelegate {
    let panel: NSPanel

    init(panel: NSPanel) {
        self.panel = panel
    }

    func control(_ control: NSControl, textView: NSTextView, doCommandBy sel: Selector) -> Bool {
        if sel == #selector(NSResponder.insertNewline(_:)) {
            let text = control.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
            if !text.isEmpty {
                saveToInbox(text: text)
            }
            NSApp.terminate(nil)
            return true
        }
        if sel == #selector(NSResponder.cancelOperation(_:)) {
            NSApp.terminate(nil)
            return true
        }
        return false
    }
}

// MARK: - Save Logic
func saveToInbox(text: String) {
    let df = DateFormatter()
    df.dateFormat = "yyyyMMdd-HHmmss"
    let timestamp = df.string(from: Date())

    df.dateFormat = "yyyy-MM-dd"
    let today = df.string(from: Date())

    // Clean title
    let firstLine = text.components(separatedBy: .newlines).first ?? text
    let illegal = CharacterSet(charactersIn: "/:\\*?\"<>|#^[]{}")
    var title = firstLine.components(separatedBy: illegal).joined()
    title = title.trimmingCharacters(in: .whitespaces)
    if title.count > 40 { title = String(title.prefix(40)) }

    let filename: String
    if title.isEmpty {
        filename = "\(timestamp).md"
    } else {
        filename = "\(timestamp) \(title).md"
    }

    let content = """
    ---
    tags:
      - inbox
    date: \(today)
    ---

    \(text)
    """
    // Remove leading spaces from heredoc-style indentation
    let lines = content.components(separatedBy: "\n").map {
        $0.hasPrefix("    ") ? String($0.dropFirst(4)) : $0
    }
    let finalContent = lines.joined(separator: "\n")

    let filePath = vaultPath.appendingPathComponent(filename)
    try? finalContent.write(to: filePath, atomically: true, encoding: .utf8)

    // Show notification
    let task = Process()
    task.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
    task.arguments = ["-e", "display notification \"Captured: \(title)\" with title \"GTD Quick Capture\""]
    try? task.run()
}

// MARK: - App Setup
let app = NSApplication.shared
app.setActivationPolicy(.accessory)

// Panel - HUD style floating window
let panelWidth: CGFloat = 560
let panelHeight: CGFloat = 52

let panel = NSPanel(
    contentRect: NSRect(x: 0, y: 0, width: panelWidth, height: panelHeight),
    styleMask: [.nonactivatingPanel, .titled, .fullSizeContentView, .hudWindow],
    backing: .buffered,
    defer: false
)

panel.isFloatingPanel = true
panel.level = .floating
panel.titlebarAppearsTransparent = true
panel.titleVisibility = .hidden
panel.isOpaque = false
panel.backgroundColor = .clear
panel.hasShadow = true
panel.isMovableByWindowBackground = true

// Center on screen
if let screen = NSScreen.main {
    let screenFrame = screen.visibleFrame
    let x = screenFrame.midX - panelWidth / 2
    let y = screenFrame.midY + screenFrame.height * 0.15
    panel.setFrameOrigin(NSPoint(x: x, y: y))
}

// Visual effect (blur background)
let container = NSView(frame: NSRect(x: 0, y: 0, width: panelWidth, height: panelHeight))

let visualEffect = NSVisualEffectView(frame: container.bounds)
visualEffect.autoresizingMask = [.width, .height]
visualEffect.blendingMode = .behindWindow
visualEffect.material = .hudWindow
visualEffect.state = .active
visualEffect.wantsLayer = true
visualEffect.layer?.cornerRadius = 14
visualEffect.layer?.masksToBounds = true
container.addSubview(visualEffect)

// Icon label
let icon = NSTextField(labelWithString: "\u{1F4E5}")
icon.font = NSFont.systemFont(ofSize: 18)
icon.frame = NSRect(x: 16, y: 11, width: 30, height: 30)
icon.isEditable = false
icon.isBezeled = false
icon.drawsBackground = false
container.addSubview(icon)

// Text field
let textField = NSTextField(frame: NSRect(x: 48, y: 11, width: panelWidth - 64, height: 30))
textField.placeholderString = "Capture to Inbox..."
textField.font = NSFont.systemFont(ofSize: 18, weight: .regular)
textField.isBezeled = false
textField.drawsBackground = false
textField.focusRingType = .none
textField.textColor = .white
textField.cell?.wraps = false
textField.cell?.isScrollable = true
container.addSubview(textField)

let delegate = CaptureFieldDelegate(panel: panel)
textField.delegate = delegate

panel.contentView = container

// Show and activate
panel.makeKeyAndOrderFront(nil)
panel.makeFirstResponder(textField)
NSApp.activate(ignoringOtherApps: true)

// Run
app.run()
