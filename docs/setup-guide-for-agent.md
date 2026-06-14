# Agent Setup Guide

Operational instructions for the `llm-gtd` skill. This guide is for Agents that can run shell commands, read vault files, and may or may not have scheduler / IM tools.

## Architecture Contract

LLM-GTD installs three layers and is produced by one Factory/Distribution layer:

| Layer | Examples | Agent responsibility |
|---|---|---|
| Agent Runtime | `SKILL.md`, rendered `AGENTS.md`, agent cron, IM MCP/Gateway, online docs | Complete what scripts cannot: scheduler jobs, IM/doc integrations, skill package updates |
| Computer Tools | Dashboard.app, launchd, QuickCapture, local scripts | Let repo scripts install/upgrade/remove; verify with doctor |
| Vault State | `00 - Inbox` through `07 - Achievements` | Preserve always; this is user data |
| Factory/Distribution | `setup/*`, `vault-template/*`, `components.json`, packaged skill | Source of setup and component upgrades |

`AGENTS.md` is canonical for GTD behavior. `SKILL.md` is the loader/action protocol.

## Host Reliability

Agents enter LLM-GTD through different hosts:

| Host type | Example | Risk | Required behavior |
|---|---|---|---|
| Workspace-bound | Claude-style session opened on the GTD vault | Low | Read `AGENTS.md` / `CLAUDE.md` and proceed. |
| Semantic skill injection | Hermes-style Agent without workspace selection | Medium | Treat generic capture phrases as ambiguous unless GTD markers are present. |

For semantic-injection-only hosts, `记一下`, `帮我记`, or `remember this` may mean GTD, memory, or wiki knowledge. If the message lacks clear GTD markers, ask whether it should go to GTD Inbox before writing vault files.

## Experience / Render View

The operational layers explain installation. The experience view explains surfaces:

- Input channels: chat, workspace Agent, skill Agent, QuickCapture, IM, import.
- Pipeline: raw Inbox item -> clarification -> GTD object in the vault.
- Render surfaces: Dashboard, Daily IM brief, Scheduling doc, IM messages.

Render surfaces must always be regenerated from a full vault scan, not from the current turn's diff.

## Setup Mode

### Step 1: Ask preferences

Ask only for values scripts cannot safely infer:

- Vault path, default `~/Documents/GTD`
- Scheduler/platform hint: `generic`, `hermes`, `openclaw`, `claude`, `cursor`
- IM / phone channel: Feishu, DingTalk, Telegram, WeCom, WeChat, or none
- Feature toggles: OKR, doc sync, side project, knowledge base
- Routine times: morning, evening, weekly
- User name/role if needed for rendered instructions

### Step 2: Run setup

```bash
python3 <repo-path>/setup/init.py \
  --vault "<vault-path>" \
  --non-interactive \
  --agent-platform generic \
  --im-platform "<feishu|dingtalk|telegram|wecom|wechat|none>" \
  --morning-time "<HH:MM>" \
  --evening-time "<HH:MM>" \
  --no-open
```

`init.py` creates the vault scaffold, renders `AGENTS.md` / `CLAUDE.md`, installs scriptable Computer Tools, writes `.llm-gtd/agent-cron-guide.md`, and initializes `.llm-gtd/component-state.json`.

### Step 3: Finish Agent Runtime

Read:

- `.llm-gtd/setup-report.md`
- `.llm-gtd/agent-cron-guide.md`
- `.llm-gtd/setup-state.json`

If scheduler tools are available, register the three Agent cron jobs. If not, report `agent_cron` as pending/manual.

If IM MCP/Gateway tools are available and doc sync is enabled, create or connect the online docs/message integration. If not, report `im_docs` as pending/manual.

### Step 4: Verify

```bash
python3 <repo-path>/setup/doctor.py --vault "<vault-path>" --check-cron --check-quickcapture --json
```

Report findings by layer: Vault State, Computer Tools, Agent Runtime.

Report render/IM findings separately: Dashboard, Daily IM brief, Scheduling doc, IM message runtime.

## Upgrade Mode

Upgrade is component-level. Do not blindly rerun full setup.

```bash
python3 <repo-path>/setup/upgrade.py --vault "<vault-path>" --check --json
python3 <repo-path>/setup/upgrade.py --vault "<vault-path>" --apply --pull-repo
```

`--check --json` returns `components`, `runtime_actions_required`, and `skill_reinstall_recommended`.

Use targeted repair when appropriate:

```bash
python3 <repo-path>/setup/upgrade.py --vault "<vault-path>" --apply --components dashboard_app --force
python3 <repo-path>/setup/upgrade.py --vault "<vault-path>" --apply --components agent_instructions
```

Rules:

- `agent_instructions` re-renders `AGENTS.md` / `CLAUDE.md` with backups.
- `dashboard_app` only rebuilds Dashboard.app.
- `dashboard` only updates Dashboard.html / exporter and runs export.
- `agent_cron_guide` marks `agent_cron: runtime_review_required`; the Agent must review or re-register scheduler jobs.
- `skill_loader` recommends skill reinstall; routine upgrade does not run `npx skills add`.

## Uninstall Mode

```bash
python3 <repo-path>/setup/uninstall.py --vault "<vault-path>"
```

The script removes scriptable Computer Tools only:

- launchd plists
- QuickCapture launch agent
- optional Dashboard.app
- optional `.llm-gtd` state with `--purge-state`

The script cannot remove Agent Runtime:

- platform agent cron jobs
- IM Gateway credentials / bots / webhooks
- online docs permissions
- installed skill package

After running the script, read `.llm-gtd/setup-state.json` and `.llm-gtd/agent-cron-guide.md`. If the current Agent has scheduler or IM tools, finish cleanup there. Otherwise report `runtime_cleanup_pending`. Never delete `00 - Inbox` through `07 - Achievements`.

## Important Notes

- Cron prompts must be self-contained; scheduled sessions have no chat memory.
- Git snapshot at 23:55 is local launchd, not Agent cron.
- Never hardcode user personal information into the repo.
- Legacy QoderWork APIs (`qoder_cron`, `小Q`, `mcp__builtin_qoderwork__action`) are deprecated.
