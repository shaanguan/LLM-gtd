---
name: llm-gtd
description: "LLM-GTD setup and daily GTD secretary. Initializes vault, Dashboard, QuickCapture, and mandatory macOS scheduled jobs, then loads AGENTS.md/CLAUDE.md for capture, morning brief, review, weekly review, doctor, or safe uninstall. Triggers: /llm-gtd, /llm-gtd-setup, 设置 GTD, 早, 回顾, 卸载 GTD."
version: 2.2.0
---

# LLM-GTD

This skill has two modes:

1. **Setup mode** — create and verify the user's GTD system.
2. **Daily runtime mode** — locate the vault, explicitly load its instruction file, then operate as the GTD secretary.

The vault instruction file (`AGENTS.md` / `CLAUDE.md`) is the GTD brain. This skill is the loader and router.

## Hard Rules

- **Scheduled jobs are mandatory on macOS.** Setup is not complete until launchd jobs are installed and verified.
- **You must execute shell commands.** Do not claim automation is installed without running the commands and reading the output.
- **Uninstall must preserve user assets.** Never delete `00 - Inbox` through `07 - Achievements` or any markdown notes inside them.

## Trigger

- Setup: `/llm-gtd`, `/llm-gtd-setup`, `设置 GTD`, `init GTD`
- Daily: `早`, `morning`, `回顾`, `review`, `周回顾`, `weekly`, `帮我记`, `inbox`
- Doctor: `GTD doctor`, `检查 GTD`
- Uninstall: `卸载 GTD`, `uninstall GTD`

## Daily Runtime Mode

1. Resolve `$VAULT_PATH` from `$GTD_VAULT`, `~/Documents/GTD`, or user input.
2. Read `.llm-gtd/setup-state.json` and locate `components.agent_instructions`.
3. Explicitly read `$VAULT_PATH/AGENTS.md` or `$VAULT_PATH/CLAUDE.md` before acting.
4. Route capture / morning / review / weekly / doctor from vault data only.

## Setup Mode

### 0. Detect existing installation

```bash
ls ~/Documents/GTD/AGENTS.md 2>/dev/null || ls ~/Documents/GTD/CLAUDE.md 2>/dev/null || \
ls "$GTD_VAULT/AGENTS.md" 2>/dev/null || ls "$GTD_VAULT/CLAUDE.md" 2>/dev/null
```

### 1. Locate or clone the repo

```bash
ls ~/Projects/LLM-gtd 2>/dev/null || ls ~/Developer/LLM-gtd 2>/dev/null || ls ~/LLM-gtd 2>/dev/null
```

If not found:

```bash
mkdir -p ~/Projects
git clone https://github.com/shaanguan/LLM-gtd.git ~/Projects/LLM-gtd
```

Store as `$REPO_PATH`.

### 2. Ask user preferences

Ask in one turn:

1. Vault location — default `~/Documents/GTD`
2. Agent platform — Hermes / OpenClaw / Claude / Cursor / Other
3. IM platform — Feishu recommended / DingTalk / Telegram / WeCom / WeChat / None
4. OKR, routine times

### 3. Run init.py

```bash
cd "$REPO_PATH"
python3 setup/init.py --vault "$VAULT_PATH" --agent-platform hermes
```

For Hermes use `--agent-platform hermes`. For Claude use `claude`. For OpenClaw use `openclaw`.

When the user already answered preferences, pass `--non-interactive` plus IM/time flags.

**Never pass** `--skip-automation`, `--skip-quickcapture`, `--no-app`, or `--no-open` in a real user setup.

Immediately read the rendered instruction file in this conversation.

### 4. Mandatory automation gate (macOS)

This step is required. Do not skip it because `init.py` already ran.

```bash
python3 "$REPO_PATH/setup/create_launchd.py" --vault "$VAULT_PATH"
python3 "$REPO_PATH/setup/create_launchd.py" --vault "$VAULT_PATH" --verify
launchctl list | grep llm-gtd
```

Expected labels:

- `com.llm-gtd.export-dashboard` — Dashboard refresh every 30 minutes
- `com.llm-gtd.git-snapshot` — vault git snapshot daily at 23:55

If `--verify` fails or `launchctl list` does not show both labels:

1. Tell the user scheduled jobs are **not** active yet.
2. Retry the install command once.
3. If still failing, give the user the exact repair commands and do **not** claim setup is complete.

On Linux, print the crontab equivalent instead and mark scheduler as `manual_required`.

### 5. Doctor verification

```bash
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-cron --check-quickcapture --json
```

Setup cannot finish unless doctor reports:

- `scheduler: ok`
- `git_snapshots: ok` (or at least export-dashboard loaded)

Summarize plainly:

- Dashboard
- Scheduler
- Git snapshots
- QuickCapture
- Online docs
- Setup report: `$VAULT_PATH/.llm-gtd/setup-report.md`

### 6. IM / docs / cold start

Continue with doc sync, Telegram, onboarding import, and final summary as before.

### 7. Final summary must mention automation

Tell the user explicitly:

> 定时任务已安装：
> - Dashboard 每 30 分钟自动刷新
> - 每晚 23:55 自动 git 快照
> 你也可以运行 `launchctl list | grep llm-gtd` 自行确认。

## Safe Uninstall

When the user asks to uninstall, run:

```bash
python3 "$REPO_PATH/setup/uninstall.py" --vault "$VAULT_PATH"
```

Optional:

```bash
python3 "$REPO_PATH/setup/uninstall.py" --vault "$VAULT_PATH" --purge-state
python3 "$REPO_PATH/setup/uninstall.py" --vault "$VAULT_PATH" --remove-dashboard-app
```

### Never delete during uninstall

- `00 - Inbox/`
- `01 - Projects/`
- `02 - Next Actions/`
- `03 - Waiting For/`
- `04 - Someday Maybe/`
- `05 - Reference/`
- `06 - Archive/`
- `07 - Achievements/`
- Any `.md` notes inside those folders

Tell the user:

> 已移除自动化（定时任务 / QuickCapture LaunchAgent）。你的任务数据仍完整保留在 vault 的 00~07 文件夹里，这是你的资产，不会被删除。
> 如需彻底不用，只需卸载 agent 里的 `llm-gtd` skill；vault 文件夹可以继续保留。

**Forbidden during uninstall:**

- `rm -rf "$VAULT_PATH"`
- deleting any folder from `00 - Inbox` through `07 - Achievements`
- deleting user markdown notes

## Pitfalls

- Hermes may skip shell unless you explicitly run commands — always run the automation gate.
- `init.py` installing launchd is not enough; you must verify with `--verify`.
- Uninstall removes automation only, never user GTD content.
