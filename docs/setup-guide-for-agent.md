# Agent Setup Guide

> Operational instructions for the `llm-gtd` skill.
> Platform-neutral: works with any agent that can run shell, install skills, and read `AGENTS.md`.

## Agent Neutrality Principles

1. **`AGENTS.md` is canonical** — the GTD brain lives in the vault, not in a specific agent product.
2. **Skill = loader** — `llm-gtd` skill explicitly reads `AGENTS.md`; it does not depend on workspace auto-injection.
3. **Platform hint is optional** — `--agent-platform` only tailors cron guide examples, not feature availability.
4. **No vendor lock-in** — do not require Hermes, OpenClaw, Claude, or Cursor by name unless the user chose that scheduler.

Legacy QoderWork APIs (`qoder_cron`, `小Q`, `mcp__builtin_qoderwork__action`) are **deprecated**.

## Two automation layers

| Layer | Purpose | Registration |
|---|---|---|
| **Local launchd** | Dashboard refresh, git snapshot | `setup/create_launchd.py` (macOS) |
| **Agent cron** | Morning / evening / weekly review | Platform scheduler, if available |

## Setup flow

### Step 1: Ask preferences

**Q1: Vault path** — default `~/Documents/GTD`

**Q2: Scheduler hint (optional)** — `generic` / `hermes` / `openclaw` / `claude` / `cursor` — for cron guide only

**Q3: IM platform** — Feishu / DingTalk / Telegram / WeCom / WeChat / None

**Q4: Feature toggles** — OKR, doc sync, side project, knowledge base

**Q5: Routine times** — morning, evening, weekly

### Step 2: Run init.py

```bash
python3 <repo-path>/setup/init.py \
  --vault "<vault-path>" \
  --non-interactive \
  --agent-platform generic \
  --im-platform "<feishu|dingtalk|telegram|wecom|wechat|none>" \
  --morning-time "<HH:MM>" \
  --evening-time "<HH:MM>"
```

`init.py` creates the vault, installs local helpers, renders `AGENTS.md` + `CLAUDE.md`, and writes `.llm-gtd/agent-cron-guide.md`.

In `--non-interactive` mode, QuickCapture is skipped by default to avoid a long Swift build in agent terminals. Pass `--install-quickcapture` only when the user wants the native hotkey built during setup.

### Step 3: Load instructions

**Skill mode (default):** use `llm-gtd` from any session. **Explicitly read** `<vault-path>/AGENTS.md` before GTD work.

**Workspace mode:** optionally open the vault as project root for auto-loaded context.

### Step 4A: Local launchd (macOS)

```bash
python3 <repo-path>/setup/create_launchd.py --vault "<vault-path>"
python3 <repo-path>/setup/create_launchd.py --vault "<vault-path>" --verify
```

### Step 4B: Register agent cron jobs (if platform supports scheduling)

```bash
python3 <repo-path>/setup/agent_cron.py --vault "<vault-path>" --platform generic --json
```

Read `.llm-gtd/agent-cron-guide.md`. Create three jobs with self-contained prompts.

**Known examples** (use only what applies):

- Hermes: prefer the `cronjob` tool with the JSON from `setup/agent_cron.py --platform hermes --json`
- OpenClaw: `openclaw cron add ... --announce`

**No scheduler?** On-demand triggers (`早`, `回顾`, `周回顾`) are the fallback. Mark `agent_cron: manual`.

### Step 5: Online docs / Telegram

If Feishu/DingTalk MCP is available, create scheduling + daily docs and backfill `AGENTS.md` §4.

### Step 6: Doctor

```bash
python3 <repo-path>/setup/doctor.py --vault "<vault-path>" --check-cron --check-quickcapture --json
```

### Step 7: Obsidian (optional)

User can open the vault folder in Obsidian; system works without it.

### Step 8: Confirm success

> **本地自动化**：Dashboard 刷新 + git 快照（macOS launchd）
> **Agent 定时任务**：若平台支持，早/晚/周回顾会主动找你；否则随时说 `早` / `回顾`
> 验证：见 `.llm-gtd/setup-report.md` 和 `agent-cron-guide.md`

## Uninstall

```bash
python3 <repo-path>/setup/uninstall.py --vault "<vault-path>"
```

Remove platform cron jobs per the guide. **Never delete** `00~07` folders.

## Important notes

- NEVER hardcode user personal info into the llm-gtd repo
- Cron prompts must be self-contained — scheduled sessions have no chat memory
- Git snapshot at 23:55 is launchd, not agent cron
