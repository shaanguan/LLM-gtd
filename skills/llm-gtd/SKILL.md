---
name: llm-gtd
description: "Personal GTD secretary. GTD, tasks, todo, inbox, capture, 待办, 项目, 下一步行动, 等待, 早, 早报, 回顾, 复盘, 周回顾, MIT, Obsidian, optional render/capture/scheduler plugins, 设置GTD, 升级GTD, 卸载GTD. Daily mode inline; setup/upgrade/uninstall/doctor in references/ loaded on demand."
version: 2.6.0
stable_contract: 1
---

# LLM-GTD Agent Runtime Loader

Product behavior, secretary judgment, routines, and daily GTD rules live in `$VAULT_PATH/AGENTS.md`. Repo scripts manage the core vault contract and optional bundled providers. The Agent must discover runtime capabilities before using them.

## Composable Block Contract

LLM-GTD is a skill-centered stack:

- **Skills:** this `llm-gtd` loader is the default GTD secretary, but another compatible skill may use the same vault contract.
- **Vaults:** user GTD state and managed templates are the durable interface. Treat the vault as shared user-owned state, not this skill's private implementation detail.
- **Capability providers:** optional plugins, framework tools, MCP servers, local apps, automation, online docs, scheduler integrations, and diagnostics can be injected around the vault.

The Agent orchestrates these blocks: use the skill to decide behavior, read/write the vault for truth, and call a provider only after discovering that the relevant capability exists.

## Capability Injection Boundary

Core defines extension points. Providers supply capabilities. The Agent discovers capabilities at runtime.

Core capability slots include `capture`, `render`, `scheduler`, `online_docs`, `messaging`, `health_check`, `backup`, and `automation`. Providers can come from this repo, another package, or the active Agent framework.

Rules:
- Discover providers from setup state, component state, files, or current tools.
- Use provider-specific commands after discovery verifies that provider.
- If a capability is unavailable, keep GTD working through the vault and record `skipped`, `pending`, `manual_verify`, `runtime_review_required`, or `runtime_cleanup_pending`.
- Load `docs/capability-contract.md` from the repo for maintenance questions about extension points.

## Agent Framework Boundary

Skill teaches behavior. Agent frameworks provide runtime.

LLM-GTD may orchestrate framework capabilities through verified tools:

- Workspace, file access, shell execution, scheduler, IM, MCP, credentials, plugin injection, and background runtime belong to the active Agent framework.
- If the framework exposes a needed capability, use it and verify the result.
- If the framework does not expose a needed tool, record `skipped`, `pending`, `runtime_review_required`, or `runtime_cleanup_pending`.
- Report external runtime changes only after provider/tool verification.

## Stable Contract

1. Match GTD-shaped messages: capture, inbox, tasks, reviews, priorities, vault, setup, upgrade, uninstall.
2. Resolve `$VAULT_PATH` and `$REPO_PATH`.
3. Read `$VAULT_PATH/AGENTS.md` before GTD work (fallback: `CLAUDE.md`).
4. Dispatch setup / upgrade / doctor / uninstall to repo scripts; load mode-specific playbook from `references/` on demand.
5. Preserve user content in `00 - Inbox` through `07 - Achievements` always.
6. Treat external runtime cleanup as complete only after provider/tool verification.

## Interface Profiles

- **desktop-workspace:** current workspace is the GTD vault or can directly read `AGENTS.md` / `CLAUDE.md`. Workspace instructions are authoritative.
- **remote-im:** user interacts through IM, mobile, gateway, scheduled job, or semantic skill injection without a vault workspace. This is platform-neutral, with OpenClaw and Hermes Agent as primary current hosts. Lower confidence; resolve paths and capabilities before writing.

If profile-specific behavior matters, load `references/profiles/desktop-workspace.md` or `references/profiles/remote-im.md`.

In `remote-im`, if the message lacks clear GTD markers (task, todo, deadline, project, next action, waiting-for, review, inbox, `GTD`, `待办`, `项目`, `DDL`, `回顾`), ask: "这是要放进 GTD Inbox，还是普通记忆/知识库？"

## Intent → Mode

| If user wants... | Mode | Where to load playbook |
|---|---|---|
| 设置 / 安装 / 初始化 / setup | setup | `references/setup.md` |
| 升级 / 更新 / upgrade | upgrade | `references/upgrade.md` |
| 卸载 / uninstall | uninstall | `references/uninstall.md` |
| 检查 / doctor / 健康检查 | doctor | `references/doctor.md` |
| anything else GTD-related | daily | **inline below** |

When unsure, prefer this skill if the user is talking about work, tasks, deadlines, or their GTD system.

For optional render or external-sync capabilities after vault changes, load `references/render-surfaces.md`.

## Resolve Paths

**Vault (`$VAULT_PATH`):** `$GTD_VAULT` → `~/Documents/GTD` → `.llm-gtd/setup-state.json` → ask once.

**Repo (`$REPO_PATH`):** read `.llm-gtd/setup-state.json` → `components.repo_path`; else `~/LLM-gtd` or `~/Projects/llm-gtd` or `~/llm-gtd`; if missing, clone `https://github.com/shaanguan/LLM-gtd.git` to `~/LLM-gtd`.

## daily (inline — most common mode)

Read `$VAULT_PATH/AGENTS.md` first. Then:

1. **Capture:** new tasks, ideas, promises → `00 - Inbox/` immediately. One file per open loop, frontmatter: `status/lifecycle: captured`, `source`, `captured_at`, `clarification_needed: true` (if ambiguous).
2. **Clarify:** propose NA / project / waiting-for / trash based on vault evidence and AGENTS.md §7 decision tree. User confirms or corrects.
3. **Organize:** move file, fill frontmatter, assign project/context/deadline.
4. **Reflect:** `早` / `回顾` / `周回顾` → scan vault, present status, batch-confirm stale items.
5. **Engage:** user chooses from available vault evidence or an injected render surface; if asked, run 4-criterion model (AGENTS.md §7.4).
6. **Refresh:** after vault changes, refresh only discovered render/external-sync capabilities per `references/render-surfaces.md`.

Key daily rules:
- Vault is the only source of truth. Read before reporting.
- Ground due dates, owners, priorities, and completion status in vault evidence or explicit user confirmation.
- Completion authority belongs to the user — do not archive without explicit confirmation.
- Within confirmed GTD context, conversation = capture. If semantic-injection intent is ambiguous, ask before writing.

## Hard Rules

- Run shell commands and verify output.
- Preserve `00 - Inbox` through `07 - Achievements`.
- Treat scheduler / messaging runtime cleanup as complete only after verification with current tools.
- `npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y` is for first install or `skill_loader` changes, not routine vault upgrades.
