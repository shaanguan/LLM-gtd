---
name: llm-gtd
description: "Personal GTD secretary runtime loader. GTD, tasks, todo, inbox, capture, 待办, 项目, 下一步行动, 等待, 早, 早报, 回顾, 复盘, 周回顾, MIT, Obsidian, Dashboard, 设置GTD, 升级GTD, 卸载GTD. Agent-facing protocol: resolve vault, read AGENTS.md, run repo scripts, and finish runtime cleanup that scripts cannot perform. For ambiguous '记一下' requests, ask whether this is GTD Inbox vs memory/knowledge before filing."
version: 2.5.2
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

1. Ask for preferences scripts cannot infer: vault path, scheduler/platform hint, IM/phone channel, feature toggles, routine times, user name/role if needed.
2. Run:

```bash
python3 "$REPO_PATH/setup/init.py" --vault "$VAULT_PATH" --non-interactive --agent-platform generic --no-open
```

3. Read `$VAULT_PATH/.llm-gtd/setup-report.md` and `$VAULT_PATH/.llm-gtd/agent-cron-guide.md`.
4. If scheduler tools are available, register morning/evening/weekly Agent cron jobs from the guide. If not, report `agent_cron` as pending/manual.
5. If IM MCP/Gateway tools are available and doc sync is enabled, create/connect docs and update the relevant runtime config. If not, report `im_docs` as pending/manual.
6. Run doctor and report layer-specific status.

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
