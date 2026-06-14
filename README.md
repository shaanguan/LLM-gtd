# LLM-GTD

> You do not need to learn GTD. Your Agent becomes the GTD expert.
>
> 你只管把脑子里的事说出来，LLM-GTD 把它们变成一个可信、可回顾、可执行的本地任务系统。

## Install in 30 Seconds

**1. Install the skill**

```bash
npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y
```

Add `-y` to skip the interactive agent picker — required when your terminal cannot send arrow keys / space / enter (e.g. Agent shell tools).

Or target one agent explicitly (also skips the picker):

```bash
npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y -a <agent>   # e.g. hermes-agent, openclaw, cursor, claude-code
```

**2. Say one sentence to your Agent**

```text
设置 GTD
```

The skill asks a few preferences, then creates everything for you:

- local GTD vault (Obsidian-ready)
- Agent instructions (`AGENTS.md`, with `CLAUDE.md` as compatibility alias)
- Dashboard + `Dashboard.app`
- QuickCapture hotkey (interactive setup installs it; non-interactive setup prints the follow-up command)
- **scheduled jobs** (Dashboard refresh every 30 min + git snapshot at 23:55)
- QUICKSTART onboarding
- Feishu / DingTalk / Telegram when credentials are available

**3. Confirm automation (two layers)**

Local launchd:

```bash
launchctl list | grep llm-gtd
```

Agent cron (if your platform supports scheduled agent tasks):

See `.llm-gtd/agent-cron-guide.md` in your vault, or run:

```bash
python3 setup/agent_cron.py --vault "$GTD_VAULT" --platform generic --json
```

You should see morning / evening / weekly GTD jobs when scheduling is supported.
Otherwise use on-demand triggers: `早`, `回顾`, `周回顾`.

**4. Try your first capture**

```text
帮我记：明天看一下 LLM-GTD Dashboard
```

You should see: say something → lands in Inbox → Dashboard updates → review later.

Fallback: download [`llm-gtd.skill`](https://github.com/shaanguan/LLM-gtd/releases/latest) if your agent installs `.skill` bundles directly.

Recommended defaults: `~/Documents/GTD`, Feishu for docs, morning brief 10:30, evening review 22:30.

Non-interactive setup skips the QuickCapture Swift build by default so agent installs do not hang. Pass `--install-quickcapture` or run the printed installer command later if you want the native hotkey.

---

LLM-GTD turns an AI agent into a senior GTD secretary. It captures messy thoughts, clarifies them into projects and next actions, reminds you at the right time, and keeps a local Markdown vault as the source of truth.

All data stays in your Obsidian vault. Dashboard, QuickCapture, scheduled reviews, Telegram/IM, and shared docs are just surfaces around that vault.

The Agent is expected to act like a high-agency secretary, not a passive form-filler: it reads the vault, interprets intent, recommends sequencing, surfaces blockers, and handles routine GTD operations while escalating irreversible or externally binding decisions.

## What You Get

- **AI GTD secretary**: the Agent understands GTD so the user does not have to.
- **Zero-friction capture**: chat, QuickCapture hotkey, Telegram, IM, paste, or import all land in Inbox first.
- **Intelligent clarification**: messy notes become projects, next actions, waiting-for items, someday ideas, or reference notes.
- **Daily operating rhythm**: say `morning`, `review`, or `weekly` to run stable GTD routines from vault data.
- **Local Dashboard**: one page for active projects, next actions, waiting-for items, stale items, and progress.
- **Native surfaces**: macOS QuickCapture, Telegram bot UX, Feishu/DingTalk docs, and local scheduled jobs.
- **Recoverable setup**: setup-state and doctor capabilities make installation resumable and debuggable.

## Uninstall Safely

Say `卸载 GTD` to your Agent, or run:

```bash
python3 setup/uninstall.py --vault "$HOME/Documents/GTD"
```

This removes automation only. **Your user data in `00 - Inbox` through `07 - Achievements` is always preserved.**

## Daily Routine

| Moment | What you say | What happens |
|---|---|---|
| Morning | `morning` / `早` | MITs, upcoming deadlines, waiting-for nudges |
| Anytime | `帮我记...` | Captured into Inbox from chat/Telegram/QuickCapture |
| Inbox sweep | `帮我过一下 Inbox` | Agent clarifies items with GTD judgement |
| Evening | `review` / `回顾` | Batch-confirm completions, archive, refresh Dashboard |
| Weekly | `weekly` / `周回顾` | Full system audit: Inbox, projects, next actions, waiting, someday |

## How It Works

```text
Storage:  Obsidian vault as local Markdown source of truth
Agent:    GTD expert skill that explicitly loads AGENTS.md from the vault
Render:   Dashboard, QuickCapture, Telegram/IM, shared docs, scheduled briefs
```

Core rule: the vault wins. Dashboard and docs are generated views.

## Requirements

- Any agent that can install the `llm-gtd` skill and read `AGENTS.md`
- Obsidian for viewing/editing the vault
- Python 3.9+
- macOS for Dashboard.app, launchd automation, and QuickCapture

## For Developers

```bash
git clone https://github.com/shaanguan/LLM-gtd.git
cd LLM-gtd
python3 setup/init.py --vault "$HOME/Documents/GTD"
python3 setup/create_launchd.py --vault "$HOME/Documents/GTD" --verify
python3 setup/doctor.py --vault "$HOME/Documents/GTD" --check-cron --check-quickcapture --json
python3 scripts/package_skill.py
```

## Links

- [Install via skills CLI](#install-in-30-seconds)
- [Download .skill fallback](https://github.com/shaanguan/LLM-gtd/releases/latest)
- [Architecture](docs/architecture.md)
- [Project tracks](docs/project-tracks.md)
- [Personal edition design](docs/personal-edition-design.md)
- [FAQ](docs/faq.md)

## License

MIT
