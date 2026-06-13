# LLM-GTD

> You do not need to learn GTD. Your Agent becomes the GTD expert.
>
> 你只管把脑子里的事说出来，LLM-GTD 把它们变成一个可信、可回顾、可执行的本地任务系统。

LLM-GTD turns an AI agent into a senior GTD secretary. It captures your messy thoughts, clarifies them into projects and next actions, reminds you at the right time, and keeps a local Markdown vault as the source of truth.

All data stays in your Obsidian vault. Dashboard, QuickCapture, scheduled reviews, Telegram/IM, and shared docs are just surfaces around that vault.

## Why This Exists

Most task systems ask you to become the system administrator of your own life: choose lists, fill fields, tag tasks, decide what is a project, and remember to review everything.

LLM-GTD flips that. The user speaks naturally. The Agent knows GTD.

```text
Messy thought → Inbox → intelligent clarification → trusted vault → Dashboard / brief / shared docs
```

The point is not another todo app. The point is a trusted external system that is easy enough to keep using.

## What You Get

- **AI GTD secretary**: the Agent understands GTD so the user does not have to.
- **Zero-friction capture**: chat, QuickCapture hotkey, Telegram, IM, paste, or import all land in Inbox first.
- **Intelligent clarification**: messy notes become projects, next actions, waiting-for items, someday ideas, or reference notes.
- **Daily operating rhythm**: say `morning`, `review`, or `weekly` to run stable GTD routines from vault data.
- **Local Dashboard**: one page for active projects, next actions, waiting-for items, stale items, and progress.
- **Native surfaces**: macOS QuickCapture, Telegram bot UX, Feishu/DingTalk docs, and local scheduled jobs.
- **Recoverable setup**: setup-state and doctor capabilities make installation resumable and debuggable.

## The Aha Moment

After setup, try this:

```text
帮我记：明天看一下 LLM-GTD Dashboard
```

The Agent writes it to Inbox, refreshes Dashboard, and shows you the loop:

```text
say something → file lands in vault → Dashboard updates → review later
```

Then paste a messy task dump. The Agent will split it into open loops first, then clarify with you.

## Install

### One-Click Agent Setup

1. Download [`llm-gtd-setup.skill`](https://github.com/shaanguan/LLM-gtd/releases/latest)
2. Install the `.skill` in OpenClaw, Hermes, Claude Desktop, Cursor, or another compatible agent
3. Say **`设置 GTD`** or **`/llm-gtd-setup`**

The setup skill asks a few preferences and then does the work:

- creates your local GTD vault
- renders the Agent instructions
- creates `Dashboard.app`
- installs QuickCapture
- registers scheduled jobs
- opens QUICKSTART
- connects Feishu/DingTalk/Telegram when credentials are available
- writes setup-state so setup can resume if interrupted
- writes `.llm-gtd/setup-report.md` so you can see whether scheduler, Git snapshots, QuickCapture, and docs are actually configured

Recommended defaults: `~/Documents/GTD`, Feishu for docs, Telegram for personal capture, morning brief at 10:30, evening review at 22:30.

## For Developers

Manual local setup:

```bash
git clone https://github.com/shaanguan/LLM-gtd.git
cd LLM-gtd
python3 setup/init.py --vault "$HOME/Documents/GTD"
python3 setup/doctor.py --vault "$HOME/Documents/GTD" --check-cron --check-quickcapture
```

Build the setup skill bundle:

```bash
python3 scripts/package_skill.py
```

This creates `dist/llm-gtd-setup.skill`, the same artifact uploaded to Releases.

Useful automation flags:

```bash
python3 setup/init.py \
  --vault "$HOME/Documents/GTD" \
  --non-interactive \
  --im-platform telegram \
  --no-open --no-app --skip-automation --skip-quickcapture
```

Machine-readable health check:

```bash
python3 setup/doctor.py --vault "$HOME/Documents/GTD" --check-cron --check-quickcapture --json
```

## How It Works

LLM-GTD uses three layers:

```text
Storage:  Obsidian vault as local Markdown source of truth
Agent:    GTD expert that reads/writes the vault and follows CLAUDE.md
Render:   Dashboard, QuickCapture, Telegram/IM, shared docs, scheduled briefs
```

Core rule: the vault wins. Dashboard and docs are generated views. The Agent must read the vault before reporting, prioritizing, archiving, or syncing.

## Daily Routine

| Moment | What you say | What happens |
|---|---|---|
| Morning | `morning` / `早` | MITs, upcoming deadlines, waiting-for nudges |
| Anytime | `帮我记...` | Captured into Inbox from chat/Telegram/QuickCapture |
| Inbox sweep | `帮我过一下 Inbox` | Agent clarifies items with GTD judgement |
| Evening | `review` / `回顾` | Batch-confirm completions, archive, refresh Dashboard |
| Weekly | `weekly` / `周回顾` | Full system audit: Inbox, projects, next actions, waiting, someday |

## Privacy And Safety

- Your vault is local Markdown.
- The vault is the source of truth; the Agent must not invent task state.
- Shared docs only expose externally relevant commitments.
- Personal notes, Someday items, and side projects do not leak into team surfaces.
- Files are archived or moved to Trash, not permanently deleted.
- Git snapshots are local by default; no automatic push.

## Requirements

- OpenClaw, Hermes, Claude Desktop, Cursor, or another agent that reads `CLAUDE.md` / `AGENTS.md`-style instructions
- Obsidian for viewing/editing the vault
- Python 3.9+
- macOS for Dashboard.app, launchd automation, and QuickCapture
- Xcode Command Line Tools for QuickCapture: `xcode-select --install`

## Links

- [Download setup skill](https://github.com/shaanguan/LLM-gtd/releases/latest)
- [Architecture](docs/architecture.md)
- [FAQ](docs/faq.md)

## License

MIT
