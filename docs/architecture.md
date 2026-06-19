# Architecture

LLM-GTD needs two orthogonal views:

- **Operational / install view:** three installed-system layers, one External Surfaces boundary, plus one Factory/Distribution layer. This explains setup, upgrade, uninstall, ownership, and what scripts can or cannot manage.
- **Experience / render view:** input channels, GTD state, and user-facing render surfaces. This explains what the user sees: Dashboard, daily IM brief, scheduling docs, and capture flows.

Do not treat one view as replacing the other. The operational view is for maintainers and Agents executing modes. The experience view is for product behavior and user-facing surfaces.

## Operational View

The installed system has three local layers, an external-surface boundary, plus one Factory/Distribution layer that produces and upgrades them. The important rule is that each `SKILL.md` mode has different authority in each layer.

```
┌────────────────────────────────────────────────────────────────────┐
│  1. Agent runtime                                                   │
│  SKILL.md loader │ AGENTS.md handbook │ agent cron │ IM MCP/Gateway │
│  Intent routing, secretary behavior, scheduled agent work, online   │
│  document/message operations.                                       │
└───────────────┬────────────────────────────────────────────────────┘
                │ reads/writes through explicit GTD rules
┌───────────────▼────────────────────────────────────────────────────┐
│  2. Computer tools                                                  │
│  QuickCapture │ Dashboard.app │ launchd jobs │ local helper scripts │
│  Desktop capture, rendering shell, local refresh, snapshots, health │
│  checks. Mostly script-installable and script-removable.            │
└───────────────┬────────────────────────────────────────────────────┘
                │ all persistent user state lives below
┌───────────────▼────────────────────────────────────────────────────┐
│  3. Vault                                                           │
│  00 - Inbox ... 07 - Achievements │ Templates │ Scripts │ .llm-gtd  │
│  User-owned source of truth. Setup and upgrade may add runtime files │
│  around it, but uninstall must never remove user GTD content.        │
└────────────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

| Layer | Owns | Can scripts fully manage it? | Persistence rule |
|---|---|---:|---|
| Agent runtime | `SKILL.md`, rendered `AGENTS.md`, cron prompts, IM MCP/Gateway doc operations | Partially | Runtime may be generated or guided, but platform cron and IM connections often require agent/user action |
| Computer tools | QuickCapture, `Dashboard.app`, launchd plists, local dashboard refresh, git snapshot jobs | Mostly | Safe to install, verify, upgrade, and remove with scripts |
| Vault | `00 - Inbox` through `07 - Achievements`, user notes, project/action/reference state | No | User data is sacred; scripts may scaffold and migrate, never destructively uninstall |
| External surfaces | Online docs, Daily IM brief, scheduling docs, IM messages, webhooks, credentials | No | Remote projections must be verified through IM MCP/Gateway; local scripts cannot truthfully create/remove them alone |
| Factory/Distribution | `tools/setup/*`, `vaults/template/*`, `skills/llm-gtd/SKILL.md`, `VERSION`, packaged `.skill` | Yes | Produces component updates; not part of user data |

Render surfaces exist in the experience view, but their implementation is distributed across operational layers:

- `Dashboard.html` is a Vault file, displayed through Dashboard.app or a browser.
- Daily IM brief and scheduling docs are External Surfaces maintained by Agent Runtime through IM MCP/Gateway.
- `export_dashboard.py` and verification scripts are Vault-local tools installed by setup.

## Experience / Render View

The experience view describes what the user and collaborators interact with.

```
Input channels
  chat / workspace Agent / semantic skill Agent / QuickCapture / IM / import
       ↓
Capture pipeline
  raw Inbox item -> clarification -> GTD object in Vault State
       ↓
Render surfaces
  Dashboard.html / Daily IM brief / Scheduling doc / messages
```

| Surface | Audience | Source of truth | Maintenance rule |
|---|---|---|---|
| Dashboard.html | User | Full vault scan | Refresh after vault changes and via local automation |
| Daily IM brief | User and selected colleagues | Full vault scan | Overwrite from current MIT / tomorrow / history rules |
| Scheduling doc | User and requesters | Full vault scan | Show only externally relevant deliverables |
| IM messages | User | Inbox and review flows | Capture into Inbox first; decisions update the vault before acknowledgement |

All render surfaces are projections. They must be regenerated from current vault state, not from the current turn's diff.

## Knowledge & Evidence Boundaries

LLM-GTD absorbs the LLM-wiki pattern as a disciplined evidence and compounding layer, not as a limit on model reasoning.

| Layer | Governs | Rule |
|---|---|---|
| Vault user state | Tasks, projects, waiting-for items, due dates, owners, priorities, completion, sync status | Must be read from current vault files before state-bearing answers or writes |
| `AGENTS.md` runtime contract | Secretary authority, routines, escalation, render/sync behavior, query audit requirements | Overrides memory and generic model behavior during LLM-GTD work |
| Model judgment | GTD interpretation, planning, secretary reasoning, prioritization advice | May exceed local wiki content, but must not invent user-specific facts |
| Repo `knowledge/gtd` | Methodology calibration, local terminology, wiki links, durable synthesis | Repo asset tracked by component hash; linked from vault, not copied into user data |
| Repo docs | Setup, upgrade, architecture, contributor maintenance | Read for maintenance contexts only; not required for ordinary daily GTD interactions |

State answers should be auditable through vault paths. Methodology answers can use model ability; when local convention matters, consult `knowledge/gtd/wiki/index.md` and the relevant page. Durable query insights can be proposed for compounding into a project page, `05 - Reference/`, or the repo knowledge base, but should not be written automatically.

Online documents have remote lifecycle in addition to render rules:

| Mode | Online document responsibility |
|---|---|
| setup | Create or connect docs only if IM tools and credentials exist; otherwise mark `im_docs: pending`. |
| daily | Verify target document identity, then full-scan vault and update selected blocks/content. |
| doctor | Check doc IDs/titles when tools exist; otherwise report manual verification. |
| upgrade | If `agent_instructions` or `doc_sync_protocol` changed, mark `im_docs: runtime_review_required`. |
| uninstall | Disable webhooks/docs/bots only with tools; otherwise mark `im_docs: runtime_cleanup_pending`. |
| fallback | Never claim remote docs were updated, created, or removed without tool evidence. |

## Host / Activation Reliability

Agents do not all enter the system the same way:

| Host type | Example | Reliability | Required behavior |
|---|---|---:|---|
| Workspace-bound | Claude-style session opened on the GTD vault | High | `AGENTS.md` / `CLAUDE.md` is loaded or directly readable; proceed from vault instructions |
| Semantic skill injection | Hermes-style Agent without workspace selection | Medium | Treat generic phrases like `记一下` as ambiguous unless GTD markers are present |

For semantic-injection-only hosts, `Skill.md` must avoid false capture. If a message could be GTD, memory, or wiki knowledge, the Agent asks whether to put it in GTD Inbox before writing vault files.

## Stable Loader Boundary

`skills/llm-gtd/SKILL.md` should remain a small loader:

1. Match GTD-shaped intent.
2. Resolve `$VAULT_PATH` and `$REPO_PATH`.
3. Read `$VAULT_PATH/AGENTS.md`.
4. Dispatch mode to repo scripts and post-script agent actions.
5. Preserve `00 - Inbox` through `07 - Achievements` on uninstall.

Do not move secretary judgment, GTD methodology, IM protocols, or cron platform details into `SKILL.md`. They belong in `vaults/template/AGENTS.md`, `.llm-gtd/agent-cron-guide.md`, and repo docs.

## Mode Matrix

| Mode | Agent runtime | Computer tools | Vault | Render / IM surfaces |
|---|---|---|---|---|
| `setup` | Ask preferences. Render `AGENTS.md`. Generate cron guide. Register platform cron/IM only with tools. | Create Dashboard.app, launchd, optional QuickCapture, local scripts. | Create scaffold and state. Never overwrite user notes. | Create/connect docs only with IM tools; otherwise mark pending. |
| `daily` | Read `AGENTS.md`, then capture, clarify, review, prioritize from evidence. | Use export/lint/preflight helpers. | Create/move/update GTD files. Archive only after confirmation. | Refresh Dashboard and enabled IM docs from full vault scan. |
| `doctor` | Check cron and IM docs; report manual verification when tools are unavailable. | Verify launchd, QuickCapture, Dashboard.app, scripts, snapshots. | Validate folders, instructions, state, version, schema. | Verify doc IDs/titles when tools exist; otherwise mark manual. |
| `upgrade` | Apply changed runtime components. Mark cron review required when guide changes. | Apply changed local-tool components only. | Apply managed runtime/template files, preserving `00` through `07`. | Review IM/doc rules when AGENTS or doc protocol changes. |
| `uninstall` | Scripts cannot remove remote runtime; Agent cleans or reports pending. | Remove scriptable local tools. | Never remove `00 - Inbox` through `07 - Achievements`. | Disable IM/doc runtime with tools, else report cleanup pending. |

## Setup Flow

Setup is a dialogue first, then scripts:

1. Agent asks for preferences that scripts cannot safely infer: vault path, phone/IM channel, scheduler platform, doc sync choice, OKR/side-project/knowledge-base toggles, routine times.
2. Agent runs `tools/setup/init.py` with those preferences.
3. Scripts install what is scriptable in the Computer tools layer: Dashboard.app, launchd jobs, optional QuickCapture, vault-local scripts.
4. Scripts scaffold the Vault layer: folders, templates, `AGENTS.md`, `CLAUDE.md`, `.llm-gtd` state.
5. Agent reads `.llm-gtd/agent-cron-guide.md` and registers platform cron jobs only when the current environment supports it.
6. Agent creates or connects IM docs through MCP/Gateway only when credentials and tools are available; otherwise it records the pending step.
7. Doctor runs at the end and reports exact remaining manual actions.

## Upgrade Flow

Upgrade is component-first and vault-safe:

1. Check repo, vault, and remote release versions.
2. Read `setup/components.json` and compare source hashes against `.llm-gtd/component-state.json`.
3. Apply only changed components, or only the components named with `--components`.
4. Preserve user notes in `00` through `07`.
5. If `agent_cron_guide` changes, mark `agent_cron` as `runtime_review_required`; scripts do not silently re-register platform cron jobs.
6. If `skill_loader` changes, report `skill_reinstall_recommended`; routine `--apply` does not install the skill package.
7. Re-read `AGENTS.md` and cron guide after upgrade.

## Uninstall Flow

Uninstall is intentionally asymmetric: scripts can remove local tools, but only the agent/user can clean up remote runtime registrations.

Scripts may remove:

- `com.llm-gtd.export-dashboard`
- `com.llm-gtd.git-snapshot`
- `com.gtd.quickcapture`
- `~/Applications/GTD Dashboard.app` when requested
- `.llm-gtd` setup state when `--purge-state` is requested

Agent/user must handle:

- Platform agent cron jobs
- IM MCP/Gateway credentials, webhooks, bots, or online docs
- Skill package removal, if the user wants to remove the loader itself

Scripts must preserve:

- `00 - Inbox`
- `01 - Projects`
- `02 - Next Actions`
- `03 - Waiting For`
- `04 - Someday Maybe`
- `05 - Reference`
- `06 - Archive`
- `07 - Achievements`

## State & Capability Tracking

`.llm-gtd/setup-state.json` is the handoff object between layers. It should track capabilities rather than pretending everything is either installed or missing:

| Capability | Meaning |
|---|---|
| `vault` | Vault scaffold exists |
| `agent_instructions` | `AGENTS.md` / `CLAUDE.md` rendered |
| `dashboard` | Dashboard file and exporter exist |
| `dashboard_app` | macOS app wrapper installed |
| `launchd` | Local scheduled jobs installed |
| `git_snapshots` | Local git snapshot job active |
| `quickcapture` | Desktop hotkey capture installed |
| `agent_cron` | Agent scheduler jobs active, pending, review required, or cleanup pending |
| `im_docs` | Online docs/message integration configured, pending, skipped, or cleanup pending |
| `agent_workspace` | Vault opened or otherwise available as agent workspace |
| `skill_loader` | Installed skill package status or review requirement |
| `gtd_knowledge_base` | Repo methodology wiki link is present and points to an existing directory |

Capability values should admit partial reality: `ok`, `pending`, `skipped`, `partial`, `manual_verify`, `runtime_review_required`, `runtime_cleanup_pending`, `manual_removal_required`, `removed`, `error`, `missing`.

`.llm-gtd/component-state.json` tracks managed component hashes by component id. It is the source for component-level upgrade decisions; `.llm-gtd/setup-state.json` remains the human/Agent capability handoff.

## Security Model

The user delegates routine GTD operations inside the vault, but not destructive control over their data or external commitments.

- Vault content is the source of truth.
- User notes are never deleted by uninstall.
- Completion and archiving require explicit user confirmation.
- External sharing, doc writes, and platform cron registration require the relevant connector/tool authority.
- Render surfaces are regenerated from a full vault scan, not from this turn's diff.
