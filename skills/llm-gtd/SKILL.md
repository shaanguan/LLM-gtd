---
name: llm-gtd
description: "Personal GTD secretary + setup + upgrade + uninstall. Capture tasks, clarify Inbox, morning brief, evening review, weekly review, MIT, next actions, waiting-for, projects, Obsidian vault, Dashboard. Triggers include: 设置GTD, 初始化, 安装GTD, 升级, 更新, 卸载, 早, 早报, 今日安排, 回顾, 复盘, 周回顾, 帮我记, 记一下, 待办, inbox, GTD, todo, capture, morning, review, weekly, upgrade, doctor, uninstall, /llm-gtd. Platform-neutral: loads AGENTS.md explicitly."
version: 2.4.0
---

# LLM-GTD

One skill for the full personal GTD lifecycle: **setup, daily runtime, upgrade, doctor, uninstall**.

Platform-neutral. Works with any agent that can run shell commands and read files.

## Intent Router (match broadly)

Use this skill when the user message **looks like GTD work**, even if they do not say exact keywords.

| Intent | Example phrases (zh / en) |
|---|---|
| **Setup** | 设置 GTD, 初始化 GTD, 安装 GTD, 配置 GTD, 帮我建 vault, setup gtd, install gtd, configure gtd, `/llm-gtd` |
| **Upgrade** | 升级 GTD, 更新 GTD, 检查更新, upgrade gtd, update gtd, new version, 版本更新 |
| **Capture** | 帮我记, 记一下, 别忘了, 待办, 任务, 提醒我这个, capture, remember, todo, add task, inbox |
| **Morning** | 早, 早报, 今日安排, 今天做什么, morning, daily brief, MIT, 最重要的事 |
| **Evening review** | 回顾, 复盘, 收尾, 今天完成了吗, review, evening, wrap up |
| **Weekly review** | 周回顾, 每周回顾, 清零 inbox, weekly, weekly review |
| **Inbox processing** | 过 inbox, 清 inbox, 处理收集箱, process inbox, clarify inbox |
| **Status / dashboard** | 看看 gtd, 打开 dashboard, 项目进展, status, what's on my plate |
| **Doctor** | 检查 GTD, GTD 健康检查, doctor, diagnose, 安装成功了吗 |
| **Uninstall** | 卸载 GTD, 删除自动化, uninstall gtd, remove gtd |

If unsure but the user is talking about **tasks, priorities, deadlines, projects, or their GTD vault**, prefer this skill.

## Context Loading

| Mode | How |
|---|---|
| **Skill mode** | Explicitly read `$VAULT_PATH/AGENTS.md` (fallback `CLAUDE.md`) before any GTD action |
| **Workspace mode** | Vault as project root may auto-load instructions; still read `AGENTS.md` if unsure |

## Hard Rules

- Execute shell commands and read output.
- **Always read `AGENTS.md`** before GTD work — never rely on chat memory alone.
- Uninstall/automation removal must preserve `00 - Inbox` through `07 - Achievements`.
- When installing/upgrading the skill: `npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y`

## Daily Runtime Mode

1. Resolve vault: `$GTD_VAULT`, `~/Documents/GTD`, or ask once.
2. Read `.llm-gtd/setup-state.json` if present.
3. **Read `$VAULT_PATH/AGENTS.md`.**
4. Act only from vault evidence.

## Setup Mode

Triggers: setup / 设置 / 初始化 / 安装 GTD

```bash
cd "$REPO_PATH"
python3 setup/init.py --vault "$VAULT_PATH" --agent-platform generic --non-interactive
```

Then macOS launchd, agent cron (if supported), and doctor. See existing setup sections in repo `docs/setup-guide-for-agent.md`.

Non-interactive setup skips QuickCapture build by default; pass `--install-quickcapture` only when requested.

## Upgrade Mode

Triggers: upgrade / 升级 / 更新 / 检查更新 / update gtd

### 1. Check for updates

```bash
python3 "$REPO_PATH/setup/upgrade.py" --vault "$VAULT_PATH" --check --json
```

Or with remote GitHub release lookup (default):

```bash
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-updates --json
```

### 2. Upgrade skill

```bash
npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y
```

### 3. Pull repo (if git checkout)

```bash
cd "$REPO_PATH" && git pull --ff-only
```

### 4. Apply vault runtime upgrade

Updates `AGENTS.md`, Dashboard template, guides, and `.llm-gtd/version`. **Does not overwrite user notes in 00~07.**

```bash
python3 "$REPO_PATH/setup/upgrade.py" --vault "$VAULT_PATH" --apply --pull-repo
```

### 5. Verify

```bash
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-cron --check-updates --json
```

Tell the user if a custom-edited `AGENTS.md` may have been refreshed — they should use git on the vault if they maintain local rule overrides.

## Safe Uninstall

```bash
python3 "$REPO_PATH/setup/uninstall.py" --vault "$VAULT_PATH"
```

Remove agent cron jobs per `.llm-gtd/agent-cron-guide.md`. Never delete user markdown in 00~07.

## Automation Layers

| Layer | Verify |
|---|---|
| launchd | `launchctl list \| grep llm-gtd` |
| agent cron | `.llm-gtd/agent-cron-guide.md` or platform scheduler CLI |

## Pitfalls

- `npx skills add` needs **`-y`** or it hangs on interactive agent picker.
- No legacy QoderWork APIs (`qoder_cron`, `小Q`).
- `init.py` / `upgrade.py` do not register agent cron by themselves — do that when the platform supports scheduling.
