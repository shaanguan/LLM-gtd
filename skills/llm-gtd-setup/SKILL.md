---
name: llm-gtd-setup
description: "LLM-GTD Setup Guide for OpenClaw, Hermes, Claude Desktop, Cursor, or compatible agents. Initializes a personal GTD system with Obsidian vault + Dashboard.app + QuickCapture + scheduled jobs + online docs/Telegram. Say 'setup GTD' or '/llm-gtd-setup' to begin."
version: 2.0.0
---

# LLM-GTD Setup

Guide the agent through setting up a complete AI GTD system for the user:
Obsidian vault + compatible agent workspace + Dashboard.app + QuickCapture + launchd automation + IM/Telegram integration.

## Trigger

User says any of:
- /llm-gtd-setup
- "setup GTD" / "设置 GTD"
- "init GTD" / "初始化 GTD"
- "uninstall GTD" → jump to Uninstall section

**Rule**: When user just types the trigger without elaboration, start Step 1 immediately.

## Steps

### 0. Detect existing installation

```bash
# Check if CLAUDE.md (the marker file) exists in common locations
ls ~/Documents/GTD/CLAUDE.md 2>/dev/null || ls "$GTD_VAULT/CLAUDE.md" 2>/dev/null
```

If found → tell user: "You already have LLM-GTD at [path]. Want to re-run setup (will preserve your data) or run a health check?"
- Re-run → continue Step 1
- Health check → `python3 $REPO_PATH/setup/doctor.py --vault "$VAULT_PATH"`

### 1. Locate or clone the repo

```bash
ls ~/Projects/LLM-gtd 2>/dev/null || ls ~/Developer/LLM-gtd 2>/dev/null || ls ~/LLM-gtd 2>/dev/null
```

If not found, clone it:

```bash
mkdir -p ~/Projects
git clone https://github.com/shaanguan/LLM-gtd.git ~/Projects/LLM-gtd
```

Store the path as `$REPO_PATH`.

### 2. Ask user preferences

Ask the following in one conversational turn (not a formal quiz):

1. **Vault location** — "Where should I create your GTD vault? Default: `~/Documents/GTD`"
2. **IM platform** — "Do you use an IM/chat tool? (Feishu recommended / DingTalk / Telegram / WeCom / WeChat / None)"
3. **OKR tracking** — "Want to link your actions to OKR objectives? (yes/no, default yes)"
4. **Routine times** — "Preferred morning brief time? Evening review? Weekly review day?"

Sensible defaults: vault=~/Documents/GTD, IM=Feishu, OKR=yes, morning=10:30, evening=22:30, weekly=Sun 21:00.

### 3. Run init.py

```bash
cd "$REPO_PATH"
python3 setup/init.py --vault "$VAULT_PATH"
```

If the user provided answers in Step 2, pass `--non-interactive` plus flags such as `--im-platform feishu` or `--im-platform telegram`, `--disable-doc-sync`, `--morning-time HH:MM`, and `--evening-time HH:MM`. Do not pass `--no-open`, `--no-app`, `--skip-automation`, or `--skip-quickcapture` for a real user setup; those are only for tests.

After init.py completes:
- `$VAULT_PATH/CLAUDE.md` is rendered
- Vault directories are created
- Dashboard.html is in place
- `.llm-gtd/version` is written

### 4. Open vault in Obsidian

Tell the user:

> "Open Obsidian → 'Open folder as vault' → select `$VAULT_PATH`.
> Enable the Templater community plugin for template support."

### 5. Add vault as agent workspace

Tell the user:

> "In OpenClaw / Hermes / Claude Desktop / Cursor:
> 1. Create or open the GTD agent workspace
> 2. Add `$VAULT_PATH` as a workspace/project folder
>
> Compatible agents will now read CLAUDE.md automatically in this workspace. That's where all your GTD rules live."

### 6. Install automation (launchd)

```bash
python3 "$REPO_PATH/setup/create_launchd.py" --vault "$VAULT_PATH"
```

`init.py` installs these by default. Re-run this command only when repairing automation:
- `com.llm-gtd.export-dashboard` — refreshes Dashboard every 30 min
- `com.llm-gtd.git-snapshot` — auto-commits vault changes at 23:55

For Linux users, print the crontab equivalent instead.

### 7. Document sync (required if user chose an IM platform)

If user selected Feishu or DingTalk:

> "For document sync to work, the agent needs access to the MCP connector for your IM platform.
>
> Configure the connector in your agent runtime. For Claude Desktop this means editing `~/Library/Application Support/Claude/claude_desktop_config.json`; for OpenClaw/Hermes use their MCP configuration flow:
> ```json
> {
>   "mcpServers": {
>     "dingtalk-docs": {
>       "command": "...",
>       "args": ["..."]
>     }
>   }
> }
> ```
>
> Once configured, I can create a scheduling doc and daily brief doc for you.
> Want me to help set that up now, or later?"

If they say now → guide through MCP server setup + create documents + backfill IDs into CLAUDE.md §4.

Use the available MCP connector to create the scheduling doc and daily brief doc. After documents are created, backfill `CLAUDE.md` §4 and QUICKSTART.html links:
```python
# Replace placeholder URLs in QUICKSTART.html with actual Feishu/DingTalk doc URLs
quickstart = Path(f"{VAULT_PATH}/QUICKSTART.html")
text = quickstart.read_text()
text = text.replace("#", f"https://alidocs.dingtalk.com/i/nodes/{scheduling_node_id}", 1)  # first # = scheduling
text = text.replace("#", f"https://alidocs.dingtalk.com/i/nodes/{daily_node_id}", 1)  # second # = daily
quickstart.write_text(text)
```

If Telegram → configure the bot connector if available. Use Telegram-native capture and prompts: inline triage buttons, reply context, voice transcription into Inbox, pinned commands for `morning/review/weekly/inbox`, and short acknowledgements after vault writes.

If WeCom/WeChat → create message-push configuration if the connector supports it; otherwise record that online docs are unavailable for that platform.

### 8. Run doctor verification

```bash
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-cron --check-quickcapture
```

Confirm zero errors. If warnings exist, fix them (doctor --fix for missing dirs).
For resumable setup, also read:
```bash
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-cron --check-quickcapture --json
```
Use `.llm-gtd/setup-state.json` and the JSON capabilities to continue from the first incomplete step.

### 9. Cold start: import todos or onboard

Ask the user:

> "System is ready! Let's get some tasks into it. Pick a way to start:
>
> **A. 7-day onboarding (recommended)** — I'll import 7 guided exercises, one per day, to build the GTD habit from scratch.
>
> **B. Tell me your tasks** — Just talk, I'll capture each one into your Inbox.
>
> **C. Give me a link or file** — Point me to your existing todo list (doc URL, file path, etc.) and I'll import it.
>
> **D. Paste a list** — Copy-paste your tasks and I'll batch-import them.
>
> Which one?"

**If A (7-day onboarding):**
Copy Day 1-7 template files from `$REPO_PATH/vault-template/00 - Inbox/` into user's vault Inbox, setting due dates to today+0 through today+6.

Tell user: "Done! 7 days of guided tasks are in your Inbox. Day 1 starts today — it's about capturing everything in your head. Just say 'morning' or 'let's do Day 1' to begin."

**If B/C/D:** Follow the import logic (brain dump / fetch URL / parse paste), write to `00 - Inbox/`.

For any cold-start import, preserve raw wording and create one Inbox file per open loop with `status: captured`, `lifecycle: captured`, `source`, `captured_at`, and `clarification_needed: true`. Then summarize what was heard before organizing.

After import, always ask: "Anything else to import from another source?"

### 10. Create Dashboard.app shortcut (macOS)

```bash
python3 "$REPO_PATH/setup/create_app.py" "$VAULT_PATH"
```

This creates a clickable .app that opens Dashboard.html. Move to ~/Applications if desired.

### 11. Final summary

> "All done! Here's your GTD system:
>
> - **Vault**: `$VAULT_PATH` (open in Obsidian)
> - **Agent workspace**: this conversation reads CLAUDE.md automatically
> - **Dashboard**: open Dashboard.html or use the .app shortcut
> - **Automation**: export_dashboard runs every 30min, git snapshot at 23:55
>
> **Daily workflow:**
> - Say 'morning' → I'll give you today's brief
> - Say 'review' or 'evening' → I'll run the evening review
> - Say anything else → I'll capture it or help you work on your tasks
>
> Try saying 'morning' now to see your first brief!"

---

## Uninstall LLM-GTD

If user wants to remove the system:

```bash
# Remove LaunchAgents
python3 "$REPO_PATH/setup/create_launchd.py" --vault "$VAULT_PATH" --uninstall

# Remove the vault from the agent workspace (manual step)
# Vault files remain — user can delete manually if desired
```

Tell user:
> "Automation removed. Your vault files are still at `$VAULT_PATH` — they're just markdown files, safe to keep or delete.
> To fully remove: delete the vault folder and remove the agent workspace/project."

---

## Pitfalls

- **Never run init.py if vault already has data without --vault flag** — it won't overwrite, but confirm with user first
- **CLAUDE.md is the brain** — if user reports odd behavior, check CLAUDE.md for stale content or unresolved placeholders
- **launchd requires user login session** — if Mac sleeps through 23:55, git snapshot runs on next wake (launchd handles this)
- **MCP server config is fragile** — if IM doc sync stops working, first check the agent MCP settings, then connector logs

## Verification

After setup, these should all pass:
```bash
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-cron --fix
```

And the user should be able to say "morning" in their GTD agent workspace and get a morning brief.
