---
name: llm-gtd
description: "LLM-GTD setup and daily GTD secretary. Platform-neutral: initializes vault, local launchd jobs, optional agent cron when the platform supports scheduling, and explicitly loads AGENTS.md for capture and routines. Triggers: /llm-gtd, 设置 GTD, 早, 回顾, 卸载 GTD."
version: 2.3.2
---

# LLM-GTD

Platform-neutral GTD secretary skill. Works with any agent that can run shell commands, install skills, and read `AGENTS.md`.

## Context Loading (two modes)

| Mode | When | How instructions load |
|---|---|---|
| **Skill mode** | Agent supports skills (recommended) | This skill explicitly reads `$VAULT_PATH/AGENTS.md` each session |
| **Workspace mode** | Vault opened as project root | `AGENTS.md` / `CLAUDE.md` auto-injected by the host |

`AGENTS.md` is canonical. `CLAUDE.md` is a compatibility alias with identical content.

## Two Automation Layers (do not confuse them)

| Layer | What | How to verify |
|---|---|---|
| **Local launchd** | Dashboard refresh every 30m, git snapshot 23:55 | `launchctl list \| grep llm-gtd` |
| **Agent cron** | Morning brief, evening review, weekly review | Your platform scheduler CLI, or `.llm-gtd/agent-cron-guide.md` |

Setup addresses both layers when the OS/platform supports them.

## Hard Rules

- Execute shell commands and read output. Do not claim jobs exist without verification.
- **Always read `$VAULT_PATH/AGENTS.md`** before GTD work — do not rely on chat memory alone.
- Register agent cron jobs **if the user's platform supports scheduled agent tasks**. Otherwise document on-demand triggers.
- Uninstall must preserve `00 - Inbox` through `07 - Achievements` and all markdown notes inside them.

## Trigger

- Setup: `/llm-gtd`, `/llm-gtd-setup`, `设置 GTD`
- Daily: `早`, `morning`, `回顾`, `review`, `周回顾`, `weekly`, `帮我记`, `inbox`
- Doctor: `GTD doctor`, `检查 GTD`
- Uninstall: `卸载 GTD`, `uninstall GTD`

## Daily Runtime Mode

1. Resolve `$VAULT_PATH` from `$GTD_VAULT`, `~/Documents/GTD`, or user input.
2. Read `.llm-gtd/setup-state.json`.
3. **Explicitly read `$VAULT_PATH/AGENTS.md`** (fallback: `CLAUDE.md`).
4. Route capture / morning / review / weekly / doctor from vault data only.

## Setup Mode

### 1. Locate repo and ask preferences

Clone `https://github.com/shaanguan/LLM-gtd.git` if needed. Ask:

1. Vault path — default `~/Documents/GTD`
2. Scheduler hint (optional) — `generic` / `hermes` / `openclaw` / `claude` / `cursor` — only affects cron guide examples
3. IM platform — Feishu, DingTalk, Telegram, WeCom, WeChat, or none
4. Morning / evening / weekly times

### 2. Run init.py

```bash
cd "$REPO_PATH"
python3 setup/init.py --vault "$VAULT_PATH" --agent-platform generic --non-interactive
```

Use a specific `--agent-platform` only when the user names their scheduler and wants tailored cron examples.

Never pass `--skip-automation` or `--skip-quickcapture` in real user setup.

`init.py` writes `.llm-gtd/agent-cron-guide.md`. Read it before registering cron jobs.

### 3. Local launchd gate (macOS)

```bash
python3 "$REPO_PATH/setup/create_launchd.py" --vault "$VAULT_PATH"
python3 "$REPO_PATH/setup/create_launchd.py" --vault "$VAULT_PATH" --verify
```

### 4. Register agent cron jobs (when platform supports scheduling)

Generate platform-specific commands:

```bash
python3 "$REPO_PATH/setup/agent_cron.py" --vault "$VAULT_PATH" --platform generic --write-guide
python3 "$REPO_PATH/setup/agent_cron.py" --vault "$VAULT_PATH" --platform <scheduler-hint> --json
```

Create **three jobs** with self-contained prompts from the guide:

- `GTD Morning Brief` — default `30 10 * * *`
- `GTD Evening Review` — default `30 22 * * *`
- `GTD Weekly Review` — default `0 21 * * 0`

Each job must load vault instructions (`llm-gtd` skill or explicit AGENTS.md read in prompt).

**Examples** (use only what matches the user's platform):

```bash
# Hermes
hermes cron create "30 10 * * *" "<prompt>" --skill llm-gtd --name "GTD Morning Brief" --deliver origin

# OpenClaw
openclaw cron add --name "GTD Morning Brief" --cron "30 10 * * *" --tz "Asia/Shanghai" \
  --session isolated --message "<prompt>" --announce
```

**No platform scheduler?** Tell the user routines work on demand via `早` / `回顾` / `周回顾`. Mark `agent_cron: manual`.

After registering jobs:

```bash
python3 - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, "$REPO_PATH/setup")
from state import update_setup_state
update_setup_state(Path("$VAULT_PATH"), steps={"register_agent_cron": "ok"}, capabilities={"agent_cron": "ok"})
PY
```

### 5. Doctor verification

```bash
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-cron --check-quickcapture --json
```

Report separately: `launchd`, `agent_cron`, `git_snapshots`, `quickcapture`.

### 6. Final summary

> **本地自动化（launchd，macOS）**
> - Dashboard 每 30 分钟刷新
> - 每晚 23:55 git 快照
> - 验证：`launchctl list | grep llm-gtd`
>
> **Agent 定时任务（若平台支持）**
> - 早间播报 / 晚间回顾 / 周回顾
> - 验证：见 `.llm-gtd/agent-cron-guide.md`
> - 无定时器时，随时说 `早` / `回顾` / `周回顾` 即可

## Safe Uninstall

```bash
python3 "$REPO_PATH/setup/uninstall.py" --vault "$VAULT_PATH"
```

Also remove agent cron jobs per `.llm-gtd/agent-cron-guide.md`.

### Never delete

- `00 - Inbox/` through `07 - Achievements/`
- any `.md` notes inside those folders

## Pitfalls

- When installing this skill via `npx skills add`, always pass **`-y`** (and optionally **`-a <agent>`**). Without it, the CLI blocks on an interactive agent picker that Agent terminals cannot operate.
- Do not use legacy QoderWork APIs (`qoder_cron`, `小Q`, `mcp__builtin_qoderwork__action`).
- `init.py` alone does not register agent cron jobs — the skill must do it when supported.
- Do not assume a specific agent brand — always load `AGENTS.md` explicitly in skill mode.
- `doctor --check-cron` checks launchd (macOS) and agent cron (best-effort per platform hint).
