# LLM-GTD

> Let AI manage your tasks — not the other way around.

An AI-powered GTD system built on **Claude Desktop + Obsidian**:

- **Local-first** — All data is Markdown in your Obsidian vault. You own everything.
- **Claude as secretary** — Captures, organizes, reminds, archives. You just talk.
- **Dashboard** — One HTML page: today's focus, waiting-for, active projects.
- **Automated** — export_dashboard + git snapshots run via launchd. Zero maintenance.
- **Optional doc sync** — Push a scheduling table to DingTalk/Feishu docs (MCP server required).

## 30-Second Overview

```
You say something → Claude writes to vault → Dashboard refreshes → You review at end of day
```

Say "morning" for today's brief. Say "review" for evening wrap-up. Say anything else and Claude captures or acts on it.

## Quick Start

```bash
# 1. Clone
git clone https://github.com/shaanguan/LLM-gtd.git ~/Projects/LLM-gtd

# 2. Run setup
python3 ~/Projects/LLM-gtd/setup/init.py

# 3. Add vault as Claude Desktop Project
#    Claude Desktop → Projects → Add folder → select your vault path

# 4. Install automation (macOS)
python3 ~/Projects/LLM-gtd/setup/create_launchd.py --vault ~/Documents/GTD

# 5. Verify
python3 ~/Projects/LLM-gtd/setup/doctor.py --vault ~/Documents/GTD --check-cron
```

Then open a conversation in your Claude Desktop project and say **"morning"**.

## Architecture

```
┌─────────────────────────────────────────┐
│           Input (you talk / hotkey)       │
│  Conversation  /  Quick Capture  /  Paste │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│         Claude Desktop (agent layer)      │
│  CLAUDE.md instructions + MCP tools       │
└─────┬────────────────────────────┬───────┘
      │ read / write / archive     │ render
┌─────▼──────────────────┐  ┌─────▼──────────────────┐
│  Obsidian Vault (data)  │  │  Outputs (you see)      │
│  Inbox / Projects / NA  │  │  Dashboard.html         │
│  WF / Archive           │  │  Shared docs (optional) │
└─────────────────────────┘  └─────────────────────────┘

Automation (launchd):
  • export_dashboard.py — every 30 min
  • git snapshot — daily 23:55
```

## Requirements

- **Claude Desktop** (with Projects feature)
- **Obsidian** (for viewing/editing vault)
- **Python 3.9+**
- **macOS** (for launchd; Linux users can use crontab)

## Daily Workflow

| Time | What happens |
|------|-------------|
| Morning | Say "morning" → Claude scans vault, reports today's MIT + upcoming + waiting |
| During day | Talk to Claude: capture ideas, process Inbox, update tasks |
| Evening | Say "review" → Claude lists today's due items for batch confirmation, archives completed |
| Weekly | Say "weekly review" → Full system audit (7 steps, ~1 hour) |

## Uninstall

```bash
# Remove automation
python3 ~/Projects/LLM-gtd/setup/create_launchd.py --vault ~/Documents/GTD --uninstall

# Remove the vault from Claude Desktop Projects (manual)
# Your vault files remain as plain Markdown — delete if you want
```

## Docs

- [Setup Guide](skills/llm-gtd-setup/SKILL.md) — Full installation walkthrough
- [Architecture](docs/architecture.md)
- [FAQ](docs/faq.md)

## License

MIT
