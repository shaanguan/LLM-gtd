# LLM-GTD

> Let AI manage your tasks — not the other way around.
> 通过一次对话，把本地 GTD vault、Dashboard、QuickCapture、定时任务和在线文档都搭起来。

An AI-powered GTD system. You do not need to know GTD: the Agent acts as a GTD expert and senior secretary. You speak naturally; it captures, clarifies, organizes, reminds, and reports. All data stays local as Markdown in your Obsidian vault.

## What You Get

- **Morning brief** — Say "morning" and get today's focus: top 3 tasks, upcoming deadlines, things you're waiting on.
- **Instant capture** — Say anything, it lands in your Inbox. Hotkey (Cmd+I) for quick capture without switching windows.
- **Intelligent clarify** — The Agent turns messy thoughts into projects, next actions, waiting-for items, someday ideas, or reference notes.
- **Evening review** — Say "review" and batch-confirm what's done. Completed items get archived automatically.
- **Dashboard** — One HTML page showing all active projects, next actions, and waiting-for items at a glance.
- **Shared docs and chat** — Push a scheduling table to Feishu/DingTalk, or use Telegram as a native capture/prompt surface.

## Install

### 一键 Agent Setup（推荐）

1. Download [`llm-gtd-setup.skill`](https://github.com/shaanguan/LLM-gtd/releases/latest) from Releases
2. Install the `.skill` in OpenClaw, Hermes, Claude Desktop, Cursor, or any compatible agent environment
3. Say **"设置 GTD"** or **"/llm-gtd-setup"**

The setup skill handles everything through conversation: create your vault, render agent instructions, create Dashboard.app, install QuickCapture, register scheduled jobs, open QUICKSTART, and create/connect shared online docs or Telegram when credentials are available. You only answer a few preferences: vault path, IM platform (Feishu recommended, Telegram supported), routine times, and whether to enable optional modules.

When it finishes, say **"morning"** — that's your first daily brief.
For cold start, paste a messy list or brain dump. The Agent will split it into Inbox items first, then clarify them with you using GTD.

To build the skill bundle from source:

```bash
python3 scripts/package_skill.py
```

This creates `dist/llm-gtd-setup.skill`, the same artifact uploaded to Releases.

### Manual local setup（开发/调试）

```bash
git clone https://github.com/shaanguan/LLM-gtd.git
cd LLM-gtd
python3 setup/init.py --vault "$HOME/Documents/GTD"
python3 setup/doctor.py --vault "$HOME/Documents/GTD" --check-cron
```

By default `init.py` tries to create the local pieces for a real user: `Dashboard.app`, launchd automation, QuickCapture, and the foreground QUICKSTART page. For scripted tests, add `--non-interactive --no-open --no-app --skip-automation --skip-quickcapture`. You can also pass `--im-platform telegram`, `--im-platform none`, `--disable-doc-sync`, `--morning-time HH:MM`, and `--evening-time HH:MM`.
For automation, `python3 setup/doctor.py --vault "$HOME/Documents/GTD" --json` returns capabilities such as vault, dashboard, scheduler, QuickCapture, online docs, and snapshots.

## How It Works

```
You say something anywhere → Inbox → Agent clarifies → vault updates → Dashboard refreshes
```

The GTD methodology has five stages. This system automates the friction out of each:

| Stage | You do | The agent does |
|---|---|---|
| **Capture** | Say it / hotkey / Telegram / paste | Writes to Inbox immediately |
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
OpenClaw / Hermes / compatible Agent + CLAUDE.md
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

- **OpenClaw, Hermes, Claude Desktop, Cursor, or another agent** that reads `CLAUDE.md` / `AGENTS.md`-style instructions
- **Obsidian** (for viewing/editing your vault)
- **Python 3.9+** (macOS ships with it)
- **macOS** (Linux: setup generates crontab instead of launchd)
- QuickCapture hotkey: **Xcode Command Line Tools** (`xcode-select --install`)

## Daily Routine

| Time | What happens |
|---|---|
| Morning | "morning" → today's MIT + upcoming + waiting |
| Day | Talk: capture ideas, process inbox, update tasks |
| Evening | "review" → batch confirm completions, archive |
| Weekly | "weekly review" → 7-step system audit (~1h) |

## Uninstall

Say **"/llm-gtd-setup"** and choose "uninstall" — it removes automation and detaches the vault. Your files remain as plain Markdown.

Manual uninstall:

```bash
python3 setup/create_launchd.py --vault "$HOME/Documents/GTD" --uninstall
```

## Links

- [Releases](https://github.com/shaanguan/LLM-gtd/releases) — download `.skill` file here
- [Architecture](docs/architecture.md)
- [FAQ](docs/faq.md)

## License

MIT
