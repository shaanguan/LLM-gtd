---
name: llm-gtd-setup
description: "LLM-GTD Setup Guide for Claude Desktop. Initializes a personal GTD system with Obsidian vault + automated dashboard + git snapshots. Say 'setup GTD' or '/llm-gtd-setup' to begin."
version: 2.0.0
---

# LLM-GTD Setup (Claude Desktop)

Guide Claude through setting up a complete AI GTD system for the user:
Obsidian vault + Claude Desktop project + launchd automation + optional IM doc sync.

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
ls ~/Projects/LLM-gtd 2>/dev/null || ls ~/llm-gtd 2>/dev/null
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
2. **IM platform** — "Do you use an IM tool with document capabilities? (DingTalk / Feishu / WeCom / WeChat / None)"
3. **OKR tracking** — "Want to link your actions to OKR objectives? (yes/no, default yes)"
4. **Routine times** — "Preferred morning brief time? Evening review? Weekly review day?"

Sensible defaults: vault=~/Documents/GTD, IM=none, OKR=yes, morning=10:30, evening=22:30, weekly=Sun 21:00.

### 3. Run init.py

```bash
cd "$REPO_PATH"
python3 setup/init.py --vault "$VAULT_PATH"
```

If user provided answers in Step 2, pass `--non-interactive` and set values via environment or edit afterward. Or run interactively and let user answer the prompts.

After init.py completes:
- `$VAULT_PATH/CLAUDE.md` is rendered
- Vault directories are created
- Dashboard.html is in place
- `.llm-gtd/version` is written

### 4. Open vault in Obsidian

Tell the user:

> "Open Obsidian → 'Open folder as vault' → select `$VAULT_PATH`.
> Enable the Templater community plugin for template support."

### 5. Add vault as Claude Desktop Project

Tell the user:

> "In Claude Desktop:
> 1. Go to Projects (left sidebar)
> 2. Create a new project or open an existing one
> 3. Add `$VAULT_PATH` as a project folder
>
> Claude will now read CLAUDE.md automatically in every conversation within this project. That's where all your GTD rules live."

### 6. Install automation (launchd)

```bash
python3 "$REPO_PATH/setup/create_launchd.py" --vault "$VAULT_PATH"
```

This installs two LaunchAgents:
- `com.llm-gtd.export-dashboard` — refreshes Dashboard every 30 min
- `com.llm-gtd.git-snapshot` — auto-commits vault changes at 23:55

For Linux users, print the crontab equivalent instead.

### 7. Document sync (optional, if user chose an IM platform)

If user selected DingTalk or Feishu:

> "For document sync to work, you'll need to configure an MCP server for your IM platform in Claude Desktop's settings.
>
> Create or edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
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

If WeCom/WeChat → skip (no doc API). Tell user doc sync isn't available for their platform.

### 8. Run doctor verification

```bash
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-cron
```

Confirm zero errors. If warnings exist, fix them (doctor --fix for missing dirs).

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
> - **Claude Project**: this conversation reads CLAUDE.md automatically
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

# Remove the vault from Claude Desktop Projects (manual step)
# Vault files remain — user can delete manually if desired
```

Tell user:
> "Automation removed. Your vault files are still at `$VAULT_PATH` — they're just markdown files, safe to keep or delete.
> To fully remove: delete the vault folder and remove the Claude Desktop project."

---

## Pitfalls

- **Never run init.py if vault already has data without --vault flag** — it won't overwrite, but confirm with user first
- **CLAUDE.md is the brain** — if user reports odd behavior, check CLAUDE.md for stale content or unresolved placeholders
- **launchd requires user login session** — if Mac sleeps through 23:55, git snapshot runs on next wake (launchd handles this)
- **MCP server config is fragile** — if IM doc sync stops working, first check Claude Desktop settings, then MCP server logs

## Verification

After setup, these should all pass:
```bash
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-cron --fix
```

And the user should be able to say "morning" in their Claude Desktop project conversation and get a GTD morning brief.
