# LLM-GTD

> Let AI manage your tasks — not the other way around.

An AI-powered GTD system. You talk, it files, reminds, and reports. All data stays local as Markdown in your Obsidian vault.

## What You Get

- **Morning brief** — Say "morning" and get today's focus: top 3 tasks, upcoming deadlines, things you're waiting on.
- **Instant capture** — Say anything, it lands in your Inbox. Hotkey (Cmd+I) for quick capture without switching windows.
- **Evening review** — Say "review" and batch-confirm what's done. Completed items get archived automatically.
- **Dashboard** — One HTML page showing all active projects, next actions, and waiting-for items at a glance.
- **Optional: shared docs** — Push a scheduling table to DingTalk/Feishu so your team sees what you're delivering.

## Install

1. Download [`llm-gtd-setup.skill`](https://github.com/shaanguan/LLM-gtd/releases/latest) from Releases
2. Open QoderWork → double-click the `.skill` file to install
3. Say **"设置 GTD"** or **"/llm-gtd-setup"**

The setup skill handles everything: creates your vault, renders the agent instructions, installs automation, configures your Dashboard. You just answer 3-4 questions (vault path, IM platform, routine times).

When it finishes, say **"morning"** — that's your first daily brief.

## How It Works

```
You say something → Agent writes to vault → Dashboard refreshes → You review at end of day
```

The GTD methodology has five stages. This system automates the friction out of each:

| Stage | You do | The agent does |
|---|---|---|
| **Capture** | Say it / hotkey / paste | Writes to Inbox immediately |
| **Clarify** | Confirm or correct | Runs decision tree: NA / project / WF / trash |
| **Organize** | Say "yes" | Moves file, fills metadata, refreshes surfaces |
| **Reflect** | Say "morning" / "review" / "weekly" | Scans vault, presents status, batch-confirms |
| **Engage** | Pick from Dashboard | Shows full picture; 4-criterion priority if asked |

**Design principle**: at every stage, your action is reduced to *saying something*.

## Architecture

```
You (talk / hotkey / paste)
        │
        ▼
Claude Desktop + CLAUDE.md (agent layer)
   │ read/write/archive         │ render
   ▼                            ▼
Obsidian Vault (data)     Dashboard + Shared docs
 Inbox / Projects / NA      (you see these)
 WF / Archive

Automation (launchd, installed by setup):
  export_dashboard — every 30 min
  git snapshot — daily 23:55
```

## Requirements

- **Claude Desktop** with Projects
- **Obsidian** (for viewing/editing your vault)
- **Python 3.9+** (macOS ships with it)
- **macOS** (Linux: setup generates crontab instead of launchd)

## Daily Routine

| Time | What happens |
|---|---|
| Morning | "morning" → today's MIT + upcoming + waiting |
| Day | Talk: capture ideas, process inbox, update tasks |
| Evening | "review" → batch confirm completions, archive |
| Weekly | "weekly review" → 7-step system audit (~1h) |

## Uninstall

Say **"/llm-gtd-setup"** and choose "uninstall" — it removes automation and detaches the vault. Your files remain as plain Markdown.

## Links

- [Releases](https://github.com/shaanguan/LLM-gtd/releases) — download `.skill` file here
- [Architecture](docs/architecture.md)
- [FAQ](docs/faq.md)

## License

MIT
