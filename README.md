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

The skill asks a few quick preferences (or `全部默认`), then creates the LLM-GTD core:

- local GTD vault (Obsidian-ready)
- Agent instructions (`AGENTS.md`, with `CLAUDE.md` as compatibility alias)
- QUICKSTART onboarding

Optional capabilities can be injected by your Agent framework, installed from other packages, or enabled from this repo's bundled examples:

- capture providers
- render providers
- scheduler providers
- messaging / online-doc providers
- backup / automation / health-check providers

**3. Optional: enable capabilities**

Bundled local automation example, if you enabled that provider:

```bash
launchctl list | grep llm-gtd
```

Bundled scheduler guide example, if you enabled or injected a scheduler provider:

See `.llm-gtd/agent-cron-guide.md` in your vault, or run:

```bash
python3 tools/setup/agent_cron.py --vault "$GTD_VAULT" --platform generic --json
```

You should see morning / evening / weekly GTD jobs only when a scheduler provider is supported and verified.
Otherwise use on-demand triggers: `早`, `回顾`, `周回顾`.

**4. Try your first capture**

```text
加到 GTD：明天整理发票
```

You should see: say something → lands in Inbox → review later. If a render provider is enabled, its output updates from the vault.

On agents that rely only on semantic skill injection, generic phrases like `记一下` may be ambiguous. The skill should ask whether the note belongs in GTD Inbox or in memory/knowledge before filing.

Fallback: download [`llm-gtd.skill`](https://github.com/shaanguan/LLM-gtd/releases/latest) if your agent installs `.skill` bundles directly.

Recommended core defaults: `~/Documents/GTD`, no required providers, morning brief 10:30, evening review 22:30. Say `全部默认` to accept all defaults in one sentence.

Setup auto-opens `QUICKSTART.html` in your browser when complete.

---

LLM-GTD turns an AI agent into a senior GTD secretary. It captures messy thoughts, clarifies them into projects and next actions, reminds you at the right time, and keeps a local Markdown vault as the source of truth.

All data stays in your Obsidian vault. Capture tools, render views, scheduled reviews, messages, and shared docs are optional providers or projections around that vault.

The Agent is expected to act like a high-agency secretary, not a passive form-filler: it reads the vault, interprets intent, recommends sequencing, surfaces blockers, and handles routine GTD operations while escalating irreversible or externally binding decisions.

## What You Get

- **AI GTD secretary**: the Agent understands GTD so the user does not have to.
- **Zero-friction capture**: chat, paste, import, or an optional capture provider can land in Inbox first.
- **Intelligent clarification**: messy notes become projects, next actions, waiting-for items, someday ideas, or reference notes.
- **Daily operating rhythm**: say `morning`, `review`, or `weekly` to run stable GTD routines from vault data.
- **Optional render providers**: generated views for active projects, next actions, waiting-for items, stale items, and progress.
- **Optional native/provider surfaces**: capture, messaging/doc integrations, scheduling, backup, and local automation can be injected or installed separately.
- **Recoverable setup**: setup-state and doctor capabilities make installation resumable and debuggable.

## Uninstall Safely

Say `卸载 GTD` to your Agent, or run:

```bash
python3 tools/setup/uninstall.py --vault "$HOME/Documents/GTD"
```

This removes selected scriptable local providers only. **Your user data in `00 - Inbox` through `07 - Achievements` is always preserved.**

## Upgrade

```bash
npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y
python3 tools/setup/upgrade.py --vault "$HOME/Documents/GTD" --check
python3 tools/setup/upgrade.py --vault "$HOME/Documents/GTD" --apply --pull-repo
```

See [Upgrading](docs/upgrading.md) for the full flow.

## Daily Routine

| Moment | What you say | What happens |
|---|---|---|
| Morning | `morning` / `早` | MITs, upcoming deadlines, waiting-for nudges |
| Anytime | `加到 GTD：...` | Captured into Inbox from chat or an optional capture provider |
| Inbox sweep | `帮我过一下 Inbox` | Agent clarifies items with GTD judgement |
| Evening | `review` / `回顾` | Batch-confirm completions, archive, refresh enabled projections |
| Weekly | `weekly` / `周回顾` | Full system audit: Inbox, projects, next actions, waiting, someday |

## How It Works

LLM-GTD is a skill-centered system with three composable blocks:

```text
Skills: Agent-facing GTD behavior and mode protocols
Vaults: durable GTD state, templates, and knowledge that other skills can reuse
Capability providers: optional capture/render/scheduler/messaging/backup/automation/diagnostic providers
```

The `llm-gtd` skill is the default GTD secretary for this repo, but the blocks are intentionally Lego-like: another skill can operate on the same vault contract, and different providers can be injected, added, or swapped around the vault as user needs change. Provider examples include render surfaces, hotkey capture, schedulers, messaging connectors, backup helpers, and diagnostics.

Operational and render views still matter under that model:

```text
Runtime view:  skill protocol -> vault contract -> local/remote tool authority
Experience view: input channels -> Inbox pipeline -> optional projections / briefs
```

Capability rule: core defines extension points, providers supply capabilities, the Agent discovers capabilities at runtime, and the vault remains source of truth.

LLM-GTD supports two interface profiles: `remote-im` for IM/mobile/gateway use, with OpenClaw and Hermes Agent as primary current hosts, and `desktop-workspace` when the vault is opened directly as an Agent workspace.

Core rule: the vault wins. Provider outputs and briefings are generated projections.

Knowledge rule: the vault is a compiled action knowledge base. Raw captures, review conclusions, project context, and useful judgments should compound into durable Markdown objects with traceable evidence, not disappear into chat history.

Maintenance writing rule: product docs define ownership and capability slots in positive terms. See [docs/writing-guidelines.md](docs/writing-guidelines.md).

## Requirements

- Any agent that can install the `llm-gtd` skill and read `AGENTS.md`
- Obsidian for viewing/editing the vault
- Python 3.9+
- macOS only for some optional bundled provider examples

## For Developers

```bash
git clone https://github.com/shaanguan/LLM-gtd.git
cd LLM-gtd
python3 tools/setup/init.py --vault "$HOME/Documents/GTD"
python3 tools/setup/init.py --vault "$HOME/Documents/GTD" --with-bundled-tools
python3 tools/setup/doctor.py --vault "$HOME/Documents/GTD" --json
python3 tools/scripts/package_skill.py
```

## Links

- [Install via skills CLI](#install-in-30-seconds)
- [Download .skill fallback](https://github.com/shaanguan/LLM-gtd/releases/latest)
- [Architecture](docs/architecture.md)
- [Capability contract](docs/capability-contract.md)
- [Action knowledge base](docs/action-knowledge-base.md)
- [Maintenance map](docs/maintenance-map.md)
- [Project tracks](docs/project-tracks.md)
- [Personal edition design](docs/personal-edition-design.md)
- [Interface profiles](docs/profiles.md)
- [Tool plugins](docs/tool-plugins.md)
- [Stable skill contract](docs/stable-skill.md)
- [Upgrading](docs/upgrading.md)
- [FAQ](docs/faq.md)

## License

MIT

## Commercial Note

Team coordination between multiple private secretaries is planned as a **separate closed-source commercial product**. It is not included in this repository. See [Project tracks](docs/project-tracks.md) for the high-level boundary only.
