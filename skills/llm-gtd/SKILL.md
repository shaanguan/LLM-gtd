---
name: llm-gtd
description: "Personal GTD secretary runtime loader. GTD, tasks, todo, inbox, capture, 待办, 项目, 下一步行动, 等待, 早, 早报, 回顾, 复盘, 周回顾, MIT, Obsidian, Dashboard, 设置GTD, 升级GTD, 卸载GTD. Agent-facing protocol: resolve vault, read AGENTS.md, run repo scripts, and finish runtime cleanup that scripts cannot perform. For ambiguous '记一下' requests, ask whether this is GTD Inbox vs memory/knowledge before filing."
version: 2.5.7
stable_contract: 1
---

# LLM-GTD Agent Runtime Loader

This skill is for the Agent. It is intentionally a small action protocol, not a GTD manual.

Product behavior, secretary judgment, routines, and daily GTD rules live in `$VAULT_PATH/AGENTS.md`. Repo scripts manage installable files and local tools. The Agent must handle runtime actions that scripts cannot complete, especially scheduler jobs and IM/Gateway integrations.

## Stable Contract

1. Match GTD-shaped messages: capture, inbox, tasks, reviews, priorities, vault, setup, upgrade, uninstall.
2. Resolve `$VAULT_PATH` and `$REPO_PATH`.
3. Read `$VAULT_PATH/AGENTS.md` before GTD work (fallback: `CLAUDE.md`).
4. Dispatch setup / upgrade / doctor / uninstall to repo scripts.
5. Preserve user content in `00 - Inbox` through `07 - Achievements` always.
6. Never claim Agent runtime cleanup is done unless you actually removed or verified it with available scheduler / IM tools.

## Activation Reliability

Agents have two host modes:

- **Workspace-bound:** the session is opened on the GTD vault or another fixed workspace that auto-loads `AGENTS.md` / `CLAUDE.md`. Treat the workspace instructions as authoritative after reading them.
- **Semantic-injection only:** the platform injects this skill because the message looked GTD-shaped. This is lower confidence. Generic capture phrases such as `记一下`, `remember this`, or `帮我记` may mean GTD, memory, or wiki knowledge.

In semantic-injection-only mode, do not auto-file ambiguous generic captures. If the message lacks clear GTD markers such as task, todo, deadline, project, next action, waiting-for, review, inbox, `GTD`, `待办`, `项目`, `DDL`, or `回顾`, ask one short clarification: "这是要放进 GTD Inbox，还是普通记忆/知识库？"

Once the user confirms GTD, continue with this skill. If they choose memory/wiki, stop GTD handling and use the appropriate memory/wiki path.

## Architecture

- **Agent Runtime:** this skill, rendered `AGENTS.md`, agent cron jobs, IM MCP/Gateway, online docs, installed skill package. Scripts can generate guides, but usually cannot remove or register external runtime state.
- **Computer Tools:** Dashboard.app, QuickCapture, launchd jobs, local vault scripts. Scripts can mostly install, verify, upgrade, and remove these.
- **Vault State:** `00 - Inbox` through `07 - Achievements`, user notes, projects, actions, waiting-for, archive, achievements. This is user-owned and must not be uninstalled.
- **External Surfaces:** online documents, IM messages, webhooks, bots, and credentials maintained through IM MCP/Gateway. Scripts can update local protocols, but the Agent must verify remote state with tools.
- **Factory/Distribution:** repo files such as `setup/*`, `vault-template/*`, `skills/llm-gtd/SKILL.md`, `VERSION`, and packaged `.skill`.

## Intent -> Mode

| If user wants... | Mode | Agent protocol |
|---|---|---|
| 设置 / 安装 / 初始化 / setup | setup | Ask preferences first, run `init.py`, read setup report and cron guide, then complete or report Agent Runtime steps. |
| 升级 / 更新 / upgrade | upgrade | Run component check, apply changed components only, then handle `runtime_actions_required`. Do not reinstall skill unless `skill_loader` changed or user asks. |
| 卸载 / uninstall | uninstall | Run local uninstall script, then remove or report pending Agent Runtime cleanup. Never delete `00` through `07`. |
| 检查 / doctor / 健康检查 | doctor | Run doctor, distinguish Vault / Computer Tools / Agent Runtime findings, and report manual cleanup or registration actions. |
| anything else GTD-related | daily | Read `AGENTS.md`, act from current vault evidence only, refresh render surfaces after vault changes. |

When unsure, prefer this skill if the user is talking about work, tasks, deadlines, or their GTD system.

## Resolve Paths

**Vault (`$VAULT_PATH`):** `$GTD_VAULT` -> `~/Documents/GTD` -> `.llm-gtd/setup-state.json` -> ask once.

**Repo (`$REPO_PATH`):** read `.llm-gtd/setup-state.json` -> `components.repo_path`; else `~/Projects/llm-gtd` or `~/llm-gtd`; if missing, clone `https://github.com/shaanguan/LLM-gtd.git` to `~/Projects/llm-gtd`.

## Mode Protocols

### setup

**Trigger:** user says `设置 GTD` / `setup GTD` with no extra context → start **Step 0** immediately.

Setup is **Agent-only**: ask in chat, pass flags to `init.py`. There is no terminal questionnaire.

**Step 0 — Detect existing installation**

```bash
ls ~/Documents/GTD/AGENTS.md ~/Documents/GTD/CLAUDE.md 2>/dev/null
ls "$GTD_VAULT/AGENTS.md" "$GTD_VAULT/CLAUDE.md" 2>/dev/null
```

If found → ask: "已有 LLM-GTD（路径 …）。要 **重跑 setup**（保留 00~07 数据）还是 **健康检查**？" Health check → `doctor.py --json`. Re-run → continue.

Clone repo if missing (store as `$REPO_PATH`):

```bash
git clone https://github.com/shaanguan/LLM-gtd.git ~/Projects/llm-gtd
```

**Step 1 — Preferences (keep it short)**

**Round 1 — ask in one message (required before `init.py`):**

1. **Vault 路径？** 默认 `~/Documents/GTD`
2. **IM / 在线文档？** 推荐飞书，可不接 — Feishu / DingTalk / Telegram / WeCom / WeChat / **暂不接入**
3. **「全部默认」可以吗？** — 若用户同意，跳过 Round 2

**Round 2 — only if user did NOT say `全部默认` / `use defaults`:**

- 改早报/晚报/周回顾时间？（默认 10:30 / 22:30 / Sun 21:00）
- 要 OKR 吗？（默认开）
- 要单独跟踪 side project 吗？（默认否；若是要问项目名）
- AGENTS.md 里显示的名字/角色？（默认 User / Knowledge Worker）
- 现在装 QuickCapture 快捷键吗？（Swift 构建 ~1 分钟；默认 **尝试安装**）

**Never ask — infer automatically:**

- `--agent-platform` → detect host (hermes / openclaw / cursor / claude / generic)
- knowledge base → on (default)
- doc sync → off when IM = 暂不接入 / none

**Step 2 — One-click `init.py`**

Real user setup must **not** pass `--no-open`, `--no-app`, `--skip-automation`, or `--skip-quickcapture`.

```bash
python3 "$REPO_PATH/setup/init.py" \
  --vault "$VAULT_PATH" \
  --agent-platform "<detected>" \
  --im-platform "<feishu|dingtalk|telegram|wecom|wechat|none>" \
  --morning-time "<HH:MM>" \
  --evening-time "<HH:MM>" \
  --weekly-time "<e.g. Sun 21:00>" \
  --user-name "<name>" \
  --user-role "<role>" \
  --install-quickcapture
```

Add when needed: `--disable-okr`, `--disable-doc-sync`, `--enable-side-project`, `--side-project-name "<name>"`.

Omit `--install-quickcapture` only if the user explicitly declined QuickCapture in Step 1.

**Step 3 — Verify local automation + QUICKSTART**

1. Confirm `QUICKSTART.html` opened (`init.py` runs `open` on macOS). If headless, tell user to open `$VAULT_PATH/QUICKSTART.html`.
2. **Mandatory launchd gate (macOS):**

```bash
python3 "$REPO_PATH/setup/create_launchd.py" --vault "$VAULT_PATH" --verify
launchctl list | grep llm-gtd
```

Expect `com.llm-gtd.export-dashboard` and `com.llm-gtd.git-snapshot`. If verify fails, retry install once; do **not** claim setup complete until fixed or user accepts manual repair.

3. Tell the user (brief):
   - **Obsidian:** Open folder as vault → `$VAULT_PATH`; optional Templater plugin
   - **Agent workspace:** add `$VAULT_PATH` in Hermes / Cursor / OpenClaw so `AGENTS.md` loads

**Step 4 — Agent Runtime**

1. Read `$VAULT_PATH/.llm-gtd/setup-report.md` and `$VAULT_PATH/.llm-gtd/agent-cron-guide.md`.
2. Register morning/evening/weekly Agent cron if scheduler tools exist; else report `agent_cron: pending`.
3. If IM ≠ none and MCP/Gateway tools exist: create/connect scheduling + daily docs, backfill doc IDs in `AGENTS.md` §4 and `QUICKSTART.html` links; else report `im_docs: pending`.
4. Run doctor:

```bash
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-cron --check-quickcapture --json
```

**Step 5 — Onboard (required)**

> 系统准备好了。第一批待办怎么进？
> **A.** 七天 GTD 冷启动（推荐） **B.** 直接告诉我 **C.** 链接或文件 **D.** 粘贴清单

| Choice | Action |
|---|---|
| **A** | `python3 "$REPO_PATH/setup/import_onboarding.py" --vault "$VAULT_PATH" --repo "$REPO_PATH"` |
| **B/C/D** | One Inbox file per open loop; `status/lifecycle: captured`, `source`, `captured_at`, `clarification_needed: true`; summarize; ask before organizing |

Ask: "还要从别的来源再导入吗？" Then `export_dashboard.py` if vault changed.

**Step 6 — Final summary + acceptance**

Tell the user:

> - **Vault:** `$VAULT_PATH`（Obsidian + Agent workspace）
> - **QUICKSTART** 应已弹出；也可开 Dashboard / GTD Dashboard.app
> - **自动化:** Dashboard 每 30 分钟刷新；23:55 git 快照；Agent cron 若已注册
>
> **日常口令:** `早` / `回顾` / `周回顾` / `加到 GTD：…`
>
> **现在试一句:** `加到 GTD：明天看一下 Dashboard` — 或说 `早` 看第一份 brief。

Setup is not done until the user completes one successful capture or Day 1 onboarding.

Mark `onboard` complete in `.llm-gtd/setup-state.json` when finished.

**Setup pitfalls**

- Do not run `init.py` before preferences or without vault path.
- Do not pass test-only skip flags for real users.
- `init.py` installing launchd is not enough — run `--verify`.
- IM doc sync needs MCP + doc IDs; missing credentials → pending, not failure.
- Never delete `00~07` during setup.

### upgrade

1. Run:

```bash
python3 "$REPO_PATH/setup/upgrade.py" --vault "$VAULT_PATH" --check --json
```

2. Inspect `components`, `skill_reinstall_recommended`, and `runtime_actions_required`.
3. Apply changed components only:

```bash
python3 "$REPO_PATH/setup/upgrade.py" --vault "$VAULT_PATH" --apply --pull-repo
```

4. For targeted repair, use:

```bash
python3 "$REPO_PATH/setup/upgrade.py" --vault "$VAULT_PATH" --apply --components dashboard_app --force
```

5. After apply, read `$VAULT_PATH/AGENTS.md` and `$VAULT_PATH/.llm-gtd/agent-cron-guide.md`.
6. If `agent_cron_guide` changed, review or re-register cron jobs. If tools are unavailable, report `agent_cron: runtime_review_required`.
7. If `skill_loader` changed, recommend `npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y`; run it only when the user wants the loader itself updated.

### uninstall

1. Run:

```bash
python3 "$REPO_PATH/setup/uninstall.py" --vault "$VAULT_PATH"
```

2. The script removes only scriptable Computer Tools. It cannot remove platform Agent cron, IM Gateway/webhooks, online doc credentials, or this installed skill package.
3. Read `$VAULT_PATH/.llm-gtd/setup-state.json` and, if present, `$VAULT_PATH/.llm-gtd/agent-cron-guide.md`.
4. If scheduler tools are available, remove the Agent cron jobs. Otherwise report `agent_cron: runtime_cleanup_pending`.
5. If IM/Gateway tools are available, disconnect or disable runtime doc/message integrations. Otherwise report `im_docs: runtime_cleanup_pending`.
6. Remove the installed skill package only if the user explicitly asked to uninstall the skill itself.
7. Confirm that `00 - Inbox` through `07 - Achievements` remain preserved.

### doctor

```bash
python3 "$REPO_PATH/setup/doctor.py" --vault "$VAULT_PATH" --check-updates --check-cron --json
```

Report issues by layer: Vault State, Computer Tools, Agent Runtime. Do not treat manual runtime verification as a local script failure.

### daily

Read `$VAULT_PATH/AGENTS.md` first. Capture new tasks into Inbox, clarify and organize from vault evidence, and refresh Dashboard / enabled render surfaces after vault changes.

## Render And IM Surface Duties

Render surfaces are the UX view of the same system. They cut across the install layers:

| Mode | Dashboard | Daily IM brief | Scheduling doc / online docs |
|---|---|---|---|
| setup | Create/render local dashboard files and app wrapper if possible. | Create/connect only if IM tools and credentials exist; otherwise mark pending. | Create/connect only if IM tools and credentials exist; otherwise mark pending. |
| daily | After vault changes, run the dashboard export from the vault. | If enabled, full-scan vault and overwrite today's brief. | If enabled, full-scan vault and update only externally relevant deliverables. |
| doctor | Verify dashboard file/exporter and local refresh jobs. | Verify configured doc IDs/titles when tools exist; otherwise report manual verification. | Verify configured doc IDs/titles when tools exist; otherwise report manual verification. |
| upgrade | Apply changed dashboard components only. | If `agent_instructions` or `doc_sync_protocol` changed, review whether IM output rules need refresh. | If `agent_instructions` or `doc_sync_protocol` changed, review whether scheduling doc rules need refresh. |
| uninstall | Local script can remove local tools only. | Agent must disable IM runtime if tools exist, else report `im_docs: runtime_cleanup_pending`. | Agent must disable doc/webhook/runtime if tools exist, else report `im_docs: runtime_cleanup_pending`. |

Always regenerate render surfaces from a full vault scan, not just this turn's edits.

Online docs are external projections, not the source of truth. The source of truth remains the vault; online docs must be checked by document ID/title before writes and updated according to `05 - Reference/doc-sync-protocol.md` when that file exists.

## Hard Rules

- Run shell commands and verify output.
- Do not delete or uninstall `00 - Inbox` through `07 - Achievements`.
- Do not say cron / IM runtime cleanup is complete unless verified with actual tools.
- `npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y` is for first install or `skill_loader` changes, not routine vault upgrades.
- No legacy QoderWork APIs (`qoder_cron`, `小Q`).
