# Agent Setup Guide

Operational instructions for the `llm-gtd` skill. This guide is for Agents that can run shell commands, read vault files, and may or may not have scheduler / IM tools.

## Architecture Contract

LLM-GTD is a skill-centered stack made from three composable blocks:

| Block | Examples | Agent responsibility |
|---|---|---|
| Skills | `skills/llm-gtd/SKILL.md`, mode playbooks, rendered `AGENTS.md` contract | Use the skill to choose behavior; complete scheduler / IM / doc actions through framework or provider tools |
| Vaults | `00 - Inbox` through `07 - Achievements`, templates, optional provider files, knowledge links | Treat as durable shared state; preserve user data always |
| Capability Providers | Agent framework tools, external plugins, or bundled examples under `tools/` | Discover at runtime; install only when selected; verify provider state with doctor |

The installed system also has runtime responsibility layers:

| Layer | Examples | Agent responsibility |
|---|---|---|
| Agent Runtime | `SKILL.md`, rendered `AGENTS.md`, agent cron, IM MCP/Gateway, online docs | Complete scheduler jobs, IM/doc integrations, and skill package updates through runtime authority |
| Capability Providers | capture, render, scheduler, messaging, online docs, backup, automation, health checks | Use only when injected/selected and verified |
| Vault State | `00 - Inbox` through `07 - Achievements` | Preserve always; this is user data |
| Factory/Distribution | `tools/setup/*`, `vaults/template/*`, `tools/setup/components.json`, packaged skill | Source of setup and component upgrades |

`AGENTS.md` is canonical for GTD behavior. `SKILL.md` is the loader/action protocol. Another compatible skill may operate on the same vault contract; providers may be injected, added, or swapped without changing the vault's core meaning. Use `init.py --core-only` for the core product; use provider installers only when the user wants those capabilities.

## Interface Profiles

Agents enter LLM-GTD through different interface profiles. Profiles are platform-neutral; providers are implementation details.

| Profile | Entry surface | Risk | Required behavior |
|---|---|---|---|
| `desktop-workspace` | Desktop Agent with the GTD vault as workspace | Low | Read `AGENTS.md` / `CLAUDE.md` and proceed from full-vault evidence. |
| `remote-im` | IM, mobile, gateway, scheduled job, or semantic skill injection | Medium | Resolve vault/tools first; treat generic capture phrases as ambiguous unless GTD markers are present. |

For `remote-im`, `记一下`, `帮我记`, or `remember this` may mean GTD, memory, or wiki knowledge. If the message lacks clear GTD markers, ask whether it should go to GTD Inbox before writing vault files.

## Experience / Render View

The operational layers explain installation. The experience view explains surfaces:

- Input channels: chat, workspace Agent, skill Agent, injected capture provider, import.
- Pipeline: raw Inbox item -> clarification -> GTD object in the vault.
- Optional projections: personal render surface, Daily brief, Scheduling doc, messages.

Render surfaces must always be regenerated from a full vault scan, not from the current turn's diff.

## Setup Mode

User says `设置 GTD` → start at **Step 0** immediately.

### Step 0: Detect existing installation

Check for `AGENTS.md` / `CLAUDE.md` in `~/Documents/GTD` or `$GTD_VAULT`. If present: offer re-run setup (preserve 00~07) or `doctor --json`. Clone repo to `~/Projects/llm-gtd` if missing.

### Step 1: Preferences (short)

**Round 1 (one message, required):**

1. Vault path (default `~/Documents/GTD`)
2. Interface profile: `desktop-workspace` or `remote-im` (remote-im primarily targets OpenClaw / Hermes Agent today)
3. Optional capabilities now or later? capture / render / scheduler / online docs / messaging / backup / automation
4. OK to use **全部默认**? Defaults mean core setup first, plugins later.

**Round 2 (only if not 全部默认):** provider choices, custom times, OKR off, side project, name/role, selected capabilities.

**Auto-infer:** agent platform from host; knowledge base on; doc sync off when IM is none.

### Step 2: One-click core init

```bash
python3 <repo-path>/tools/setup/init.py \
  --vault "<vault-path>" \
  --agent-platform "<detected>" \
  --im-platform "<feishu|dingtalk|telegram|wecom|wechat|none>" \
  --core-only
```

Add time/name flags only when user customized. Omit `--core-only` only when the user explicitly wants the bundled local tool recipe.

### Step 3: QUICKSTART + optional providers

- Confirm QUICKSTART opened; else tell user to open it.
- If a bundled local automation provider is enabled: run its verify command.
- Brief Obsidian + Agent workspace instructions

### Step 4: Agent Runtime / integrations

Read setup-report. Read agent-cron-guide only if a scheduler provider generated it. Register recurring routines only if the scheduler capability is enabled and tools exist. Connect online docs/messages only if that capability is enabled and provider tools are available. Run doctor `--json`.

### Step 5: Onboard A/B/C/D

Seven-day cold start / brain dump / link / paste — see skill Step 5.

### Step 6: Final summary

Vault + QUICKSTART + optional capability summary. Ask user to try `加到 GTD：…` or `早`. Mark `onboard` complete.

## Upgrade Mode

Upgrade is component-level. Use component apply rather than a full setup rerun.

```bash
python3 <repo-path>/tools/setup/upgrade.py --vault "<vault-path>" --check --json
python3 <repo-path>/tools/setup/upgrade.py --vault "<vault-path>" --apply --pull-repo
```

`--check --json` returns `components`, `runtime_actions_required`, and `skill_reinstall_recommended`.

Use targeted repair when appropriate:

```bash
python3 <repo-path>/tools/setup/upgrade.py --vault "<vault-path>" --apply --components dashboard_app --force
python3 <repo-path>/tools/setup/upgrade.py --vault "<vault-path>" --apply --components agent_instructions
```

Rules:

- `agent_instructions` re-renders `AGENTS.md` / `CLAUDE.md` with backups.
- Provider components only update their own provider files.
- Bundled render examples such as `dashboard` only update that render provider and run its exporter.
- `agent_cron_guide` marks `agent_cron: runtime_review_required`; the Agent must review or re-register scheduler jobs.
- `skill_loader` recommends skill reinstall; routine upgrade does not run `npx skills add`.

## Uninstall Mode

```bash
python3 <repo-path>/tools/setup/uninstall.py --vault "<vault-path>"
```

The script removes selected scriptable local providers only:

- selected local automation provider files
- selected local capture provider files
- selected local render app/provider files
- optional `.llm-gtd` state with `--purge-state`

Agent Runtime cleanup uses framework or provider tools:

- platform agent cron jobs
- IM Gateway credentials / bots / webhooks
- online docs permissions
- installed skill package

After running the script, read `.llm-gtd/setup-state.json` and `.llm-gtd/agent-cron-guide.md`. If the current Agent has scheduler or IM tools, finish cleanup there. Otherwise report `runtime_cleanup_pending`. Preserve `00 - Inbox` through `07 - Achievements`.

## Important Notes

- Cron prompts must be self-contained; scheduled sessions have no chat memory.
- Git snapshot at 23:55, when enabled, is a local automation provider, not Agent scheduler runtime.
- Keep user personal information in the user's vault or runtime state, not in the repo.
- Deprecated QoderWork API names (`qoder_cron`, `小Q`, `mcp__builtin_qoderwork__action`) are compatibility history.
