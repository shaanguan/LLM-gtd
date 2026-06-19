# Architecture

LLM-GTD is a **skill product**: it teaches an Agent how to help a user build, manage, and use GTD. The core product is the skill plus the GTD vault contract.

The canonical repo model is three composable Lego blocks:

```text
skills/  -> Agent-facing GTD behavior and mode protocols
vaults/  -> durable GTD state contract, templates, and knowledge
tools/   -> optional provider examples, installers, adapters, and diagnostics
```

The default core is `skills/llm-gtd` + `vaults/template`. Provider examples under `tools/` can be enabled, replaced, or supplied by an Agent framework. Another skill can operate on a compatible GTD vault. The vault remains the durable contract between them.

The capability rule is:

```text
Core defines extension points.
Providers supply capabilities.
Agent discovers capabilities at runtime.
Vault remains the source of truth.
```

See [Capability Contract](capability-contract.md) for the stable extension-point model.

LLM-GTD has two operating views:

- **Operational / install view:** three installed-system layers, one External Surfaces boundary, plus one Factory/Distribution layer. This explains setup, upgrade, uninstall, ownership, and script authority.
- **Experience / projection view:** input channels, GTD state, and user-facing projections. This explains what the user sees: render surfaces, daily briefs, scheduling docs, messages, and capture flows.

The repository model explains composition and replaceability. The operational view explains runtime authority. The experience view explains user-facing behavior.

## Composable Blocks

| Block | Path | Owns | Replaceability rule |
|---|---|---|---|
| Skills | `skills/` | Agent-facing intent routing, mode protocols, and runtime obligations | `llm-gtd` is the default skill, not the only possible GTD skill |
| Vaults | `vaults/` and installed user vaults | GTD folder contract, templates, managed runtime files, methodology links, user state | Vault state is the stable interface; multiple skills or tools may read/write it through explicit rules |
| Capability Providers | `tools/`, external packages, or Agent framework tools | optional setup recipes, upgrade helpers, doctor, local apps, automation, capture, render, online docs, schedulers | Providers are injected around the vault; add, remove, or swap them while preserving the vault contract |

The main dependency direction is:

```text
Skill chooses behavior
  -> reads/writes Vault contract
  -> discovers capability providers at runtime
  -> calls a provider only when evidence proves it is enabled
```

Scripts manage files and local providers within their authority. Agent frameworks and remote providers manage their own runtime.

## Product Boundary

| Part | Category | Distribution rule |
|---|---|---|
| `llm-gtd` skill loader and mode playbooks | Core contract | Install as the skill package |
| GTD vault contract and `AGENTS.md` secretary handbook | Core contract | Render into each user's vault |
| GTD methodology knowledge | Shared reference | Link from repo; keep user data in the vault |
| Render providers | Capability provider | Can visualize GTD or other vaults |
| Capture providers | Capability provider | Capture target should be configurable: GTD Inbox, knowledge inbox, or other vault entrypoint |
| Automation providers | Capability provider | Install only when user chooses or framework injects automation |
| Scheduler providers | Host adapter or integration | Register only with scheduler tools and user intent |
| Online docs / messaging providers | Capability provider | Connect only with credentials and tool evidence |

`tools/setup/init.py --core-only` is the preferred core recipe. The bundled-tools recipe remains available as one possible provider bundle for users who want a batteries-included local setup.

## Operational View

The installed system has three runtime responsibility layers, an external-surface boundary, plus one Factory/Distribution layer that produces and upgrades them. The important rule is that each `SKILL.md` mode has different authority in each layer.

```
┌────────────────────────────────────────────────────────────────────┐
│  1. Skill / Agent runtime                                           │
│  SKILL.md loader │ AGENTS.md handbook │ agent cron │ IM MCP/Gateway │
│  Intent routing, secretary behavior, scheduled agent work, online   │
│  document/message operations.                                       │
└───────────────┬────────────────────────────────────────────────────┘
                │ reads/writes through explicit GTD rules
┌───────────────▼────────────────────────────────────────────────────┐
│  2. Capability providers                                             │
│  Capture │ Render │ Scheduler │ Online docs │ Automation │ Backup    │
│  Optional injected or installed providers discovered at runtime.     │
│  Local selected providers can be managed by setup scripts.           │
└───────────────┬────────────────────────────────────────────────────┘
                │ all persistent user state lives below
┌───────────────▼────────────────────────────────────────────────────┐
│  3. Vault                                                           │
│  00 - Inbox ... 07 - Achievements │ Templates │ .llm-gtd │ optional Scripts │
│  User-owned source of truth. Setup and upgrade may add runtime files │
│  around it; uninstall preserves user GTD content.                   │
└────────────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

| Layer | Owns | Can scripts fully manage it? | Persistence rule |
|---|---|---:|---|
| Skill / Agent runtime | `SKILL.md`, rendered `AGENTS.md`, cron prompts, IM MCP/Gateway doc operations | Partially | Runtime may be generated or guided, but platform cron and IM connections often require agent/user action |
| Capability providers | capture, render, scheduler, messaging, online docs, health check, backup, automation providers | For local selected providers | Install, verify, upgrade, and remove through the provider's authority |
| Vault | `00 - Inbox` through `07 - Achievements`, user notes, project/action/reference state | No | User data is sacred; scripts scaffold and migrate around it |
| External surfaces | Online docs, daily briefs, scheduling docs, messages, webhooks, credentials | No | Remote projections are verified through provider tools |
| Factory/Distribution | `tools/setup/*`, `vaults/template/*`, `skills/llm-gtd/SKILL.md`, `VERSION`, packaged `.skill` | Yes | Produces component updates; not part of user data |

Render surfaces exist in the experience view, but their implementation is distributed across operational layers:

- Personal render surfaces are provider outputs; a Dashboard file/app is only one example.
- Daily briefs, messages, and scheduling docs are External Surfaces maintained only when messaging/online-doc providers are injected and verified.
- Exporters and verification scripts are provider files installed only when the relevant provider is selected or externally injected.

## Experience / Render View

The experience view describes what the user and collaborators interact with.

```
Input channels
  chat / workspace Agent / semantic skill Agent / injected capture provider / import
       ↓
Capture pipeline
  raw Inbox item -> clarification -> GTD object in Vault State
       ↓
Optional projections
  personal render surface / daily brief / scheduling doc / messages
```

| Projection | Audience | Source of truth | Maintenance rule |
|---|---|---|---|
| Personal render surface | User | Full vault scan | Refresh after vault changes only when a render provider exists |
| Daily brief | User and selected recipients | Full vault scan | Overwrite from current MIT / tomorrow / history rules only when a messaging/render provider exists |
| Scheduling doc | User and requesters | Full vault scan | Show only externally relevant deliverables only when an online-doc provider exists |
| Message | User | Inbox and review flows | Capture into Inbox first; decisions update the vault before acknowledgement |

All projections are provider outputs regenerated from current vault state. If no provider exists, the vault and current Agent response remain sufficient.

## Knowledge & Evidence Boundaries

LLM-GTD absorbs the LLM-wiki pattern as a disciplined evidence and compounding layer, not as a limit on model reasoning.

In product terms: the GTD vault is a **compiled, compounding, auditable personal action knowledge base**. Raw input is not left as chat residue; it is continuously compiled into structured GTD objects, project context, references, review conclusions, and logs. See [Action Knowledge Base](action-knowledge-base.md) for the detailed contract.

| Layer | Governs | Rule |
|---|---|---|
| Vault user state | Tasks, projects, waiting-for items, due dates, owners, priorities, completion, sync status | Must be read from current vault files before state-bearing answers or writes |
| `AGENTS.md` runtime contract | Secretary authority, routines, escalation, render/sync behavior, query audit requirements | Overrides memory and generic model behavior during LLM-GTD work |
| Model judgment | GTD interpretation, planning, secretary reasoning, prioritization advice | May exceed local wiki content while grounding user-specific facts in vault evidence |
| Repo `vaults/knowledge/gtd` | Methodology calibration, local terminology, wiki links, durable synthesis | Repo asset tracked by component hash; linked from vault, not copied into user data |
| Repo docs | Setup, upgrade, architecture, contributor maintenance | Maintenance context for repo work; daily GTD starts from the vault |

State answers should be auditable through vault paths. Methodology answers can use model ability; when local convention matters, consult `vaults/knowledge/gtd/wiki/index.md` and the relevant page. Durable query insights can be proposed for compounding into a project page, `05 - Reference/`, or the repo knowledge base after the Agent has a clear target and appropriate user consent.

Inspired by plain, open knowledge formats, LLM-GTD-managed knowledge should remain Markdown-first, frontmatter-readable, linkable, and portable across Agent frameworks and capability providers.

Online documents have remote lifecycle in addition to render rules:

| Mode | Online document / messaging responsibility |
|---|---|
| setup | Create/connect only if a provider, credentials, and target identity exist; otherwise mark skipped or pending. |
| daily | Verify target identity, then full-scan vault and update selected blocks/content. |
| doctor | Check provider targets when tools exist; otherwise report manual verification. |
| upgrade | If `agent_instructions` or projection protocol changed, mark the capability `runtime_review_required`. |
| uninstall | Disable webhooks/docs/bots only with provider tools; otherwise mark `runtime_cleanup_pending`. |
| fallback | Report the current provider state and continue from the vault. |

## Interface Profiles

Agents enter the system through different interfaces. Interface profiles describe the user's operating surface without naming a specific platform.

| Profile | Entry surface | Vault relationship | Required behavior |
|---|---|---|---|
| `desktop-workspace` | Desktop Agent with the GTD vault as workspace | High evidence: `AGENTS.md` / `CLAUDE.md` and vault folders are directly readable | Read workspace instructions, then do full-vault operations and local-tool verification |
| `remote-im` | IM, mobile, gateway, scheduled job, or semantic skill injection; primary current hosts are OpenClaw and Hermes Agent | Lower evidence: vault path and capabilities may need resolution | Resolve vault/tools first; treat generic phrases like `记一下` as ambiguous unless GTD markers are present |

For `remote-im`, `Skill.md` must avoid false capture. If a message could be GTD, memory, or wiki knowledge, the Agent asks whether to put it in GTD Inbox before writing vault files.

## Stable Loader Boundary

`skills/llm-gtd/SKILL.md` should remain a small loader:

1. Match GTD-shaped intent.
2. Resolve `$VAULT_PATH` and `$REPO_PATH`.
3. Read `$VAULT_PATH/AGENTS.md`.
4. Dispatch mode to repo scripts and post-script agent actions.
5. Preserve `00 - Inbox` through `07 - Achievements` on uninstall.

Keep `SKILL.md` focused on loading and routing. Secretary judgment belongs in `vaults/template/AGENTS.md`; provider details belong in generated guides, provider docs, and repo docs.

## Mode Matrix

| Mode | Skill / Agent runtime | Capability providers | Vault | Projections |
|---|---|---|---|---|
| `setup` | Ask preferences. Render `AGENTS.md`. Register platform runtime only with injected tools. | Core recipe starts with the vault contract; install or connect explicitly selected providers. | Create scaffold and state while preserving user notes. | Create/connect only when a projection provider is selected, injected, and verified; otherwise mark skipped or pending. |
| `daily` | Read `AGENTS.md`, then capture, clarify, review, prioritize from evidence. | Use helpers only when provider discovery proves they exist. | Create/move/update GTD files. Archive only after confirmation. | Refresh enabled projections from full vault scan. |
| `doctor` | Check runtime capabilities; report manual verification when tools are unavailable. | Verify discovered providers only. | Validate folders, instructions, state, version, schema. | Verify projection targets when tools exist; otherwise mark manual. |
| `upgrade` | Apply changed runtime components. Mark runtime review required when provider-facing protocols change. | Apply enabled or explicitly selected provider components only. | Apply managed runtime/template files, preserving `00` through `07`. | Review projection rules when AGENTS or projection protocol changes. |
| `uninstall` | Remote runtime cleanup follows provider/framework authority; Agent cleans or reports pending only for enabled capabilities. | Remove selected scriptable providers only. | Preserve `00 - Inbox` through `07 - Achievements`. | Disable projections with provider tools, else report cleanup pending. |

## Setup Flow

Setup is a dialogue first, then scripts:

1. Agent asks for preferences that belong to the user: vault path, interface profile, desired optional capabilities, OKR/side-project/knowledge-base toggles, routine times.
2. Agent runs `tools/setup/init.py --core-only` for the core recipe; bundled provider examples are added when the user selects them.
3. Scripts install selected bundled providers only; externally injected providers are discovered rather than installed by core.
4. Scripts scaffold the Vault layer: folders, templates, `AGENTS.md`, `CLAUDE.md`, `.llm-gtd` state.
5. If a scheduler capability is selected or injected, Agent registers routines only when the current framework exposes scheduler tools.
6. Agent creates or connects external projections only when provider credentials and tools are available; otherwise it records skipped or pending.
7. Doctor runs at the end and reports exact remaining manual actions.

## Upgrade Flow

Upgrade is component-first and vault-safe:

1. Check repo, vault, and remote release versions.
2. Read `tools/setup/components.json` and compare source hashes against `.llm-gtd/component-state.json`.
3. Apply only changed components, or only the components named with `--components`.
4. Preserve user notes in `00` through `07`.
5. If provider-facing guidance changes, mark the relevant capability as `runtime_review_required`.
6. If `skill_loader` changes, report `skill_reinstall_recommended`; routine `--apply` does not install the skill package.
7. Re-read `AGENTS.md` and cron guide after upgrade.

## Uninstall Flow

Uninstall is capability-aware: scripts remove selected local providers, while remote runtime registrations are handled by their providers. Provider removal is separate from the core contract and user vault data.

Scripts may remove:

- `com.llm-gtd.export-dashboard`
- `com.llm-gtd.git-snapshot`
- `com.gtd.quickcapture`
- `~/Applications/GTD Dashboard.app` when requested
- `.llm-gtd` setup state when `--purge-state` is requested

Agent/user must handle when those providers were enabled:

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
| `render` | Render provider exists and is verified |
| `dashboard` | Compatibility alias for an existing render provider state |
| `capture` | Capture provider exists and is verified |
| `quickcapture` | Compatibility alias for an existing capture provider state |
| `automation` | Automation provider exists and is verified |
| `launchd` | Compatibility alias for an existing automation provider state |
| `backup` | Backup/snapshot provider exists and is verified |
| `git_snapshots` | Compatibility alias for an existing backup provider state |
| `scheduler` | Scheduler provider active, pending, review required, or cleanup pending |
| `agent_cron` | Compatibility alias for an existing scheduler provider state |
| `online_docs` | Online-doc/message provider configured, pending, skipped, or cleanup pending |
| `im_docs` | Compatibility alias for an existing online-doc/message provider state |
| `agent_workspace` | Vault opened or otherwise available as agent workspace |
| `skill_loader` | Installed skill package status or review requirement |
| `gtd_knowledge_base` | Repo methodology wiki link is present and points to an existing directory |

Capability values should admit partial reality: `ok`, `pending`, `skipped`, `partial`, `manual_verify`, `runtime_review_required`, `runtime_cleanup_pending`, `manual_removal_required`, `removed`, `error`, `missing`.

`.llm-gtd/component-state.json` tracks managed component hashes by component id. It is the source for component-level upgrade decisions; `.llm-gtd/setup-state.json` remains the human/Agent capability handoff.

## Security Model

The user delegates routine GTD operations inside the vault, but not destructive control over their data or external commitments.

- Vault content is the source of truth.
- Uninstall preserves user notes.
- Completion and archiving require explicit user confirmation.
- External sharing, doc writes, and platform cron registration require the relevant connector/tool authority.
- Render surfaces are regenerated from a full vault scan, not from this turn's diff.
