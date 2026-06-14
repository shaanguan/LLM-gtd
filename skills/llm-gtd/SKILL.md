---
name: llm-gtd
description: "Personal GTD secretary loader. Tasks, todo, inbox, capture, 帮我记, 记一下, 待办, 早, 早报, 回顾, 复盘, 周回顾, MIT, projects, 设置GTD, 初始化, 安装, 升级, 更新, 卸载, setup, upgrade, review, morning, weekly, GTD, Obsidian, Dashboard. Platform-neutral: read vault AGENTS.md for all GTD behavior."
version: 2.4.1
stable_contract: 1
---

# LLM-GTD (stable loader)

**This file is intentionally thin.** It routes intent, resolves paths, reads `AGENTS.md`, and calls repo scripts. GTD rules, routines, and judgment live in the **vault**, not here.

Do not duplicate setup/upgrade/cron detail in this skill — read `$VAULT_PATH/AGENTS.md` and repo docs after loading the vault.

## Stable contract (v1 — change rarely)

1. **Match** any GTD-shaped message: tasks, capture, inbox, review, priorities, vault, setup, upgrade, uninstall.
2. **Resolve** `$VAULT_PATH` and `$REPO_PATH` (see below).
3. **Read** `$VAULT_PATH/AGENTS.md` before any GTD action (fallback: `CLAUDE.md`).
4. **Dispatch** to the repo script for setup / upgrade / doctor / uninstall; otherwise obey `AGENTS.md`.
5. **Preserve** user notes in `00 - Inbox` … `07 - Achievements` on uninstall.

## Intent → mode

| If user wants… | Mode | Action |
|---|---|---|
| 设置 / 安装 / 初始化 / setup | setup | `init.py` → `doctor.py` — details in `docs/setup-guide-for-agent.md` |
| 升级 / 更新 / upgrade | upgrade | `upgrade.py --check` then `--apply --pull-repo` — **vault-first, no skill reinstall** |
| 卸载 / uninstall | uninstall | `uninstall.py` |
| 检查 / doctor / 健康检查 | doctor | `doctor.py --check-updates --check-cron --json` |
| anything else GTD-related | daily | read `AGENTS.md`, act on vault evidence only |

When unsure, prefer this skill if the user is talking about work, tasks, deadlines, or their GTD system.

## Resolve paths

**Vault (`$VAULT_PATH`):** `$GTD_VAULT` → `~/Documents/GTD` → `.llm-gtd/setup-state.json` → ask once.

**Repo (`$REPO_PATH`):** read `.llm-gtd/setup-state.json` → `components.repo_path`; else `~/Projects/llm-gtd` or `~/llm-gtd`; if missing, `git clone https://github.com/shaanguan/LLM-gtd.git` to `~/Projects/llm-gtd`.

## Mode commands

```bash
# setup
python3 "$REPO_PATH/setup/init.py" --vault "$VAULT_PATH" --non-interactive --agent-platform generic --no-open

# upgrade (default for “升级 GTD”)
python3 "$REPO_PATH/setup/upgrade.py" --vault "$VAULT_PATH" --check --json
python3 "$REPO_PATH/setup/upgrade.py" --vault "$VAULT_PATH" --apply --pull-repo

# doctor
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-updates --check-cron --json

# uninstall
python3 "$REPO_PATH/setup/uninstall.py" --vault "$VAULT_PATH"
```

After setup or upgrade, read `$VAULT_PATH/AGENTS.md` and `$VAULT_PATH/.llm-gtd/agent-cron-guide.md` for automation steps not covered above.

## Hard rules

- Run shell commands; verify output.
- **`npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y`** only when installing the skill the first time — not for routine vault upgrades.
- No legacy QoderWork APIs (`qoder_cron`, `小Q`).

## Maintainer note

Product changes go to `vault-template/AGENTS.md`, `setup/*`, and `VERSION`. Change this skill only when routing or path resolution must change. See `docs/stable-skill.md`.
