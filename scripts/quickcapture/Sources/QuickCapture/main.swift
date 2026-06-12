import Cocoa
import Carbon

// MARK: - Config
// __INBOX_DIR__ is replaced by init.py with the user's actual vault inbox path.
// If running from source without replacement, defaults to ~/Documents/GTD/00 - Inbox
let inboxDir: URL = {
    let placeholder = "__INBOX_DIR__"
    if placeholder.hasPrefix("__") {
        return FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Documents/GTD/00 - Inbox")
    }
    return URL(fileURLWithPath: placeholder)
}()
let draftPath = "/tmp/gtd-capture-draft.txt"
let togglePath = "/tmp/gtd-toggle"
let pidPath = "/tmp/gtd-quick-capture.pid"

// MARK: - Global Hotkey Callback
func hotKeyHandler(
    nextHandler: EventHandlerCallRef?,
    theEvent: EventRef?,
    userData: UnsafeMutableRawPointer?
) -> OSStatus {
    guard let userData = userData, let theEvent = theEvent else {
        return OSStatus(eventNotHandledErr)
    }
    let del = Unmanaged<AppDelegate>.fromOpaque(userData).takeUnretainedValue()
    var kind: UInt32 = 0
    GetEventParameter(theEvent, EventParamName(kEventParamDirectObject),
                      EventParamType(typeUInt32), nil,
                      MemoryLayout<UInt32>.size, nil, &kind)
    let eventKind = Int(GetEventKind(theEvent))
    if eventKind == kEventHotKeyPressed {
        DispatchQueue.main.async { del.hotKeyPressed() }
    } else if eventKind == kEventHotKeyReleased {
        DispatchQueue.main.async { del.hotKeyReleased() }
    }
    return noErr
}

// MARK: - AppDelegate
class AppDelegate: NSObject, NSApplicationDelegate {
    var panel: NSPanel!
    var textView: NSTextView!
    var scrollView: NSScrollView!
    var timer: Timer?
    var hotKeyRef: EventHotKeyRef?
    var hotKeyIsDown = false  // track key state to ignore repeats

    func applicationDidFinishLaunching(_ notification: Notification) {
        try? "\(ProcessInfo.processInfo.processIdentifier)"
            .write(toFile: pidPath, atomically: true, encoding: .utf8)
        setupPanel()
        registerGlobalHotKey()
        startPoller()
    }

    // MARK: - Hotkey state
    func hotKeyPressed() {
        if hotKeyIsDown { return }  // ignore key-repeat events
        hotKeyIsDown = true
        toggle()
    }

    func hotKeyReleased() {
        hotKeyIsDown = false
    }

    // MARK: - Register Global Hotkey ⌘I
    func registerGlobalHotKey() {
        let hotKeyID = EventHotKeyID(
            signature: OSType(0x47544400),
            id: 1
        )
        // Listen to both pressed AND released
        var eventTypes = [
            EventTypeSpec(
                eventClass: OSType(kEventClassKeyboard),
                eventKind: UInt32(kEventHotKeyPressed)
            ),
            EventTypeSpec(
                eventClass: OSType(kEventClassKeyboard),
                eventKind: UInt32(kEventHotKeyReleased)
            )
        ]
        let selfPtr = Unmanaged.passUnretained(self).toOpaque()
        InstallEventHandler(
            GetApplicationEventTarget(),
            hotKeyHandler,
            2,
            &eventTypes,
            selfPtr,
            nil
        )
        RegisterEventHotKey(
            UInt32(kVK_ANSI_I),
            UInt32(cmdKey),
            hotKeyID,
            GetApplicationEventTarget(),
            0,
            &hotKeyRef
        )
    }

    // MARK: - Panel
    func setupPanel() {
        let W: CGFloat = 600
        let H: CGFloat = 160
        let headerH: CGFloat = 40
        let pad: CGFloat = 16

        panel = NSPanel(
            contentRect: NSRect(x: 0, y: 0, width: W, height: H),
            styleMask: [.titled, .fullSizeContentView, .nonactivatingPanel],
            backing: .buffered,
            defer: false
        )
        panel.titlebarAppearsTransparent = true
        panel.titleVisibility = .hidden
        panel.isOpaque = false
        panel.backgroundColor = .clear
        panel.hasShadow = true
        panel.level = .floating
        panel.isMovableByWindowBackground = true
        panel.hidesOnDeactivate = false
        panel.animationBehavior = .utilityWindow

        if let screen = NSScreen.main {
            let sf = screen.visibleFrame
            let x = sf.origin.x + (sf.width - W) / 2
            let y = sf.origin.y + sf.height * 0.65
            panel.setFrameOrigin(NSPoint(x: x, y: y))
        }

        // --- Glass background ---
        let blur = NSVisualEffectView(frame: NSRect(x: 0, y: 0, width: W, height: H))
        blur.autoresizingMask = [.width, .height]
        blur.blendingMode = .behindWindow
        blur.material = .hudWindow
        blur.state = .active
        blur.wantsLayer = true
        blur.layer?.cornerRadius = 14
        blur.layer?.masksToBounds = true

        // === Header ===
        let headerY = H - headerH

        let iconLabel = NSTextField(labelWithString: "📥")
        iconLabel.font = .systemFont(ofSize: 20)
        iconLabel.sizeToFit()
        let iconW = iconLabel.frame.width
        let iconH = iconLabel.frame.height
        iconLabel.frame = NSRect(
            x: pad + 2,
            y: headerY + (headerH - iconH) / 2,
            width: iconW,
            height: iconH
        )
        blur.addSubview(iconLabel)

        let title = NSTextField(labelWithString: "GTD 收集箱")
        title.font = .systemFont(ofSize: 14, weight: .medium)
        title.textColor = .secondaryLabelColor
        title.sizeToFit()
        let titleH = title.frame.height
        title.frame = NSRect(
            x: pad + iconW + 8,
            y: headerY + (headerH - titleH) / 2,
            width: title.frame.width,
            height: titleH
        )
        title.isEditable = false
        title.isBezeled = false
        title.drawsBackground = false
        blur.addSubview(title)

        let hint = NSTextField(labelWithString: "⌘I 收起  ⏎ 保存  ⇧⏎ 换行  esc 丢弃")
        hint.font = .monospacedSystemFont(ofSize: 11, weight: .regular)
        hint.textColor = .tertiaryLabelColor
        hint.alignment = .right
        hint.sizeToFit()
        let hintH = hint.frame.height
        hint.frame = NSRect(
            x: W - hint.frame.width - pad,
            y: headerY + (headerH - hintH) / 2,
            width: hint.frame.width,
            height: hintH
        )
        hint.isEditable = false
        hint.isBezeled = false
        hint.drawsBackground = false
        blur.addSubview(hint)

        let sep = NSBox(frame: NSRect(x: pad, y: headerY - 1, width: W - pad * 2, height: 1))
        sep.boxType = .separator
        blur.addSubview(sep)

        // === Text area ===
        let textAreaY: CGFloat = pad - 2
        let textAreaH: CGFloat = headerY - 1 - pad * 2 + 6
        let textAreaX: CGFloat = pad + 2
        let textAreaW: CGFloat = W - (pad + 2) * 2

        scrollView = NSScrollView(frame: NSRect(x: textAreaX, y: textAreaY, width: textAreaW, height: textAreaH))
        scrollView.hasVerticalScroller = false
        scrollView.hasHorizontalScroller = false
        scrollView.drawsBackground = false
        scrollView.borderType = .noBorder

        let captureTV = CaptureTextView(frame: NSRect(x: 0, y: 0, width: textAreaW, height: textAreaH))
        captureTV.font = .systemFont(ofSize: 16, weight: .regular)
        captureTV.textColor = .labelColor
        captureTV.drawsBackground = false
        captureTV.isRichText = false
        captureTV.allowsUndo = true
        captureTV.isAutomaticQuoteSubstitutionEnabled = false
        captureTV.isAutomaticDashSubstitutionEnabled = false
        captureTV.isAutomaticTextReplacementEnabled = false
        captureTV.textContainer?.widthTracksTextView = true
        captureTV.textContainer?.size = NSSize(width: textAreaW, height: 10000)
        captureTV.isHorizontallyResizable = false
        captureTV.isVerticallyResizable = true
        captureTV.insertionPointColor = .labelColor
        captureTV.textContainerInset = NSSize(width: 0, height: 2)

        let paraStyle = NSMutableParagraphStyle()
        paraStyle.lineSpacing = 6
        paraStyle.paragraphSpacing = 4
        captureTV.defaultParagraphStyle = paraStyle
        captureTV.typingAttributes = [
            .font: NSFont.systemFont(ofSize: 16, weight: .regular),
            .foregroundColor: NSColor.labelColor,
            .paragraphStyle: paraStyle
        ]

        captureTV.placeholderText = "记录想法…"
        captureTV.onSubmit = { [weak self] in self?.submit() }
        captureTV.onCancel = { [weak self] in self?.cancel() }

        textView = captureTV
        scrollView.documentView = textView
        blur.addSubview(scrollView)

        panel.contentView = blur
    }

    // MARK: - Show / Hide / Cancel
    func show() {
        loadDraft()
        panel.makeKeyAndOrderFront(nil)
        panel.makeFirstResponder(textView)
        NSApp.activate(ignoringOtherApps: true)
    }

    func hide() {
        // ⌘I hide: save draft, next ⌘I restores it
        saveDraft()
        panel.orderOut(nil)
    }

    func cancel() {
        // Esc: discard everything
        textView.string = ""
        clearDraft()
        panel.orderOut(nil)
    }

    func submit() {
        let text = textView.string.trimmingCharacters(in: .whitespacesAndNewlines)
        if !text.isEmpty {
            saveToInbox(text: text)
        }
        textView.string = ""
        clearDraft()
        panel.orderOut(nil)
    }

    func toggle() {
        if panel.isVisible {
            hide()
        } else {
            show()
        }
    }

    // MARK: - Inbox
    func saveToInbox(text: String) {
        let df = DateFormatter()
        df.dateFormat = "yyyyMMdd-HHmmss"
        let ts = df.string(from: Date())
        df.dateFormat = "yyyy-MM-dd"
        let today = df.string(from: Date())

        let illegal = CharacterSet(charactersIn: "/:\\*?\"<>|#^[]{}")
        var title = text.components(separatedBy: .newlines).first ?? text
        title = title.components(separatedBy: illegal).joined()
            .trimmingCharacters(in: .whitespaces)
        if title.count > 40 { title = String(title.prefix(40)) }

        let filename = title.isEmpty ? "\(ts).md" : "\(ts) \(title).md"
        let content = "---\ntags:\n  - inbox\ndate: \(today)\n---\n\n\(text)\n"
        let filePath = inboxDir.appendingPathComponent(filename)
        try? content.write(to: filePath, atomically: true, encoding: .utf8)

        DispatchQueue.global().async {
            let task = Process()
            task.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
            task.arguments = ["-e",
                "display notification \"已收录：\(title)\" with title \"GTD\""]
            try? task.run()
        }
    }

    // MARK: - Draft
    func saveDraft() {
        let text = textView.string
        if !text.isEmpty {
            try? text.write(toFile: draftPath, atomically: true, encoding: .utf8)
        } else {
            try? FileManager.default.removeItem(atPath: draftPath)
        }
    }

    func loadDraft() {
        if let draft = try? String(contentsOfFile: draftPath, encoding: .utf8), !draft.isEmpty {
            textView.string = draft
            textView.setSelectedRange(NSRange(location: draft.count, length: 0))
        } else {
            textView.string = ""
        }
    }

    func clearDraft() {
        try? FileManager.default.removeItem(atPath: draftPath)
    }

    // MARK: - Poller (fallback for touch /tmp/gtd-toggle)
    func startPoller() {
        timer = Timer.scheduledTimer(withTimeInterval: 0.05, repeats: true) { [weak self] _ in
            if FileManager.default.fileExists(atPath: togglePath) {
                try? FileManager.default.removeItem(atPath: togglePath)
                DispatchQueue.main.async {
                    self?.toggle()
                }
            }
        }
    }
}

// MARK: - Custom TextView
class CaptureTextView: NSTextView {
    var onSubmit: (() -> Void)?
    var onCancel: (() -> Void)?
    var placeholderText: String?

    override func keyDown(with event: NSEvent) {
        let isReturn = event.keyCode == 36
        let isEsc = event.keyCode == 53
        let isShift = event.modifierFlags.contains(.shift)

        if isReturn {
            if isShift {
                insertNewlineIgnoringFieldEditor(nil)
            } else {
                onSubmit?()
            }
            return
        }

        if isEsc {
            onCancel?()
            return
        }

        super.keyDown(with: event)
    }

    override func draw(_ dirtyRect: NSRect) {
        super.draw(dirtyRect)

        if string.isEmpty, let placeholder = placeholderText {
            let paraStyle = NSMutableParagraphStyle()
            paraStyle.lineSpacing = 6
            let attrs: [NSAttributedString.Key: Any] = [
                .foregroundColor: NSColor.placeholderTextColor,
                .font: font ?? NSFont.systemFont(ofSize: 16, weight: .regular),
                .paragraphStyle: paraStyle
            ]
            let str = NSAttributedString(string: placeholder, attributes: attrs)
            str.draw(at: NSPoint(x: textContainerInset.width + 5, y: textContainerInset.height))
        }
    }

    override func becomeFirstResponder() -> Bool {
        needsDisplay = true
        return super.becomeFirstResponder()
    }

    override func didChangeText() {
        super.didChangeText()
        needsDisplay = true
    }
}

// MARK: - Main
let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let delegate = AppDelegate()
app.delegate = delegate
app.run()
