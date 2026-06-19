# Maintenance Map

Use this map when you know what behavior changed but do not remember which file owns it.

## First Question: Which Block?

LLM-GTD is maintained as three composable blocks:

| Block | Use it for | Canonical paths |
|---|---|---|
| Skills | Agent intent, mode protocol, runtime obligations, ambiguity policy | `skills/llm-gtd/SKILL.md`, `skills/llm-gtd/references/*` |
| Vaults | GTD state contract, templates, secretary handbook, render source files, methodology knowledge | `vaults/template/*`, `vaults/knowledge/gtd/*` |
| Capability Providers | Optional injected or bundled providers: capture, render, scheduler, messaging, online docs, backup, automation, health checks | `tools/setup/*`, `tools/scripts/*`, `tools/resources/*`, `docs/tool-plugins.md`, `docs/capability-contract.md` |

External surfaces are provider-managed projections and credentials. Skills can operate through verified integrations; local scripts manage only the providers and files within their authority.

## Then Ask: Which View?

LLM-GTD has two orthogonal views:

| View | Use it for | Canonical file |
|---|---|---|
| Operational / install view | setup, upgrade, uninstall, component ownership, script limits, external-surface boundaries | `docs/architecture.md` |
| Experience / projection view | capture channels, render providers, briefs, scheduling docs, messages, what the user sees | `vaults/template/AGENTS.md` |

The operational view explains who can manage a component. The experience view explains what surfaces must be updated after vault changes.

## Change Routing

| If you change... | Edit first | Then check |
|---|---|---|
| Agent trigger, mode protocol, semantic-injection ambiguity | `skills/llm-gtd/SKILL.md` | `docs/stable-skill.md`, package with `tools/scripts/package_skill.py` |
| Daily GTD behavior, secretary authority, Inbox processing | `vaults/template/AGENTS.md` | Demo vault and component upgrade for `agent_instructions` |
| Product boundary between core and providers | `docs/architecture.md`, `docs/tool-plugins.md`, `docs/capability-contract.md` | `README.md`, `skills/llm-gtd/references/setup.md` |
| Dashboard UI/data projection | `tools/plugins/dashboard/vault-assets/*` | `tools/setup/components.json` component `dashboard` |
| Online doc lifecycle or remote cleanup | `docs/architecture.md`, `skills/llm-gtd/SKILL.md` | `setup-state` capability `im_docs` |
| IM brief or scheduling-doc behavior | `vaults/template/AGENTS.md`, `tools/plugins/online-docs/vault-assets/*` | component `doc_sync_protocol` |
| Setup questions or initial install flow | `tools/setup/init.py` | `docs/setup-guide-for-agent.md`, setup-state fields |
| Component upgrade behavior | `tools/setup/components.json`, `tools/setup/components.py`, `tools/setup/upgrade.py` | `.llm-gtd/component-state.json` semantics |
| Local macOS automation | `tools/setup/create_launchd.py` | `doctor.py`, uninstall behavior |
| Dashboard.app wrapper | `tools/setup/create_app.py`, `tools/resources/*` | component `dashboard_app` |
| QuickCapture | `tools/setup/install_quickcapture.py`, `tools/scripts/quickcapture/*` | component `quickcapture` |
| Safe uninstall | `tools/setup/uninstall.py` | `Skill.md` uninstall protocol, setup-state capability labels |
| Doctor/reporting | `tools/setup/doctor.py` | layer labels in architecture docs |

## Interface Profile Checklist

When changing triggers or capture wording, check both interface profiles:

- **desktop-workspace:** the Agent is in a GTD vault workspace and can rely on `AGENTS.md` / `CLAUDE.md`.
- **remote-im:** the Agent is reached through IM, mobile, gateway, scheduled job, or semantic skill injection. Generic phrases such as `记一下` require a clarification unless GTD intent is explicit.

Tests should protect the profile names, the ambiguity rule in `Skill.md`, and the daily capture behavior in `AGENTS.md`.

## Projection Capability Checklist

When changing any mode, ask whether each optional capability is affected. Concrete providers are examples:

| Capability | Setup | Daily | Doctor | Upgrade | Uninstall |
|---|---|---|---|---|---|
| `render` | connect selected provider or skip | refresh from full vault scan | verify discovered provider | apply enabled/selected component only | remove local provider only |
| `messaging` | connect or pending | send/update from full vault scan | verify if tools exist | review if protocol changed | disable or mark pending |
| `online_docs` | connect or pending | update external deliverables only | verify if tools exist | review if protocol changed | disable or mark pending |

`doc_sync_protocol` is a managed component. If that component changes, upgrade marks `im_docs` for runtime review so the responsible provider can verify or migrate remote online documents.

If tools or credentials are unavailable, record the projection state as pending/manual and continue from vault evidence.

## Release Checklist

1. Bump `VERSION` when repo behavior changes.
2. Bump `skills/llm-gtd/SKILL.md` version when Agent mode protocol or activation policy changes.
3. Update `tools/setup/components.json` when adding or moving managed components.
4. Run `python3 -m unittest discover -s tests`.
5. Run `python3 tools/scripts/package_skill.py`.
6. Confirm packaged skill contains the intended version.
7. Scan product docs with [Writing Guidelines](writing-guidelines.md) before release.
