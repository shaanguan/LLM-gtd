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

User says `设置 GTD` → start at **Step 0** immediately.

### Step 0: Detect existing installation

Check for `AGENTS.md` / `CLAUDE.md` in `~/Documents/GTD` or `$GTD_VAULT`. If present: offer re-run setup (preserve 00~07) or `doctor --json`. Clone repo to `~/Projects/llm-gtd` if missing.

### Step 1: Preferences (short)

**Round 1 (one message, required):**

1. Vault path (default `~/Documents/GTD`)
2. IM / online docs — Feishu recommended, or none
3. OK to use **全部默认**?

**Round 2 (only if not 全部默认):** custom times, OKR off, side project, name/role, QuickCapture opt-out.

**Auto-infer:** agent platform from host; knowledge base on; doc sync off when IM is none.

### Step 2: One-click init

Do **not** pass `--no-open`, `--no-app`, `--skip-automation`, or `--skip-quickcapture` for real users.

```bash
python3 <repo-path>/setup/init.py \
  --vault "<vault-path>" \
  --agent-platform "<detected>" \
  --im-platform "<feishu|dingtalk|telegram|wecom|wechat|none>" \
  --install-quickcapture
```

Add time/name flags only when user customized. Omit `--install-quickcapture` only if user declined QuickCapture.

### Step 3: Verify automation + QUICKSTART

- Confirm QUICKSTART opened; else tell user to open it.
- macOS: `create_launchd.py --verify` + `launchctl list | grep llm-gtd`
- Brief Obsidian + Agent workspace instructions

### Step 4: Agent Runtime

Read setup-report and agent-cron-guide. Register Agent cron if tools exist. Connect IM docs if IM ≠ none and MCP available. Run doctor `--json`.

### Step 5: Onboard A/B/C/D

Seven-day cold start / brain dump / link / paste — see skill Step 5.

### Step 6: Final summary

Vault + QUICKSTART + automation summary. Ask user to try `加到 GTD：…` or `早`. Mark `onboard` complete.

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
