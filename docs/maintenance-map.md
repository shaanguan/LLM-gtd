# Maintenance Map

Use this map when you know what behavior changed but do not remember which file owns it.

## First Question: Which View?

LLM-GTD has two orthogonal views:

| View | Use it for | Canonical file |
|---|---|---|
| Operational / install view | setup, upgrade, uninstall, component ownership, script limits, external-surface boundaries | `docs/architecture.md` |
| Experience / render view | capture channels, Dashboard, IM brief, scheduling docs, what the user sees | `vaults/template/AGENTS.md` |

The operational view explains who can manage a component. The experience view explains what surfaces must be updated after vault changes.

## Change Routing

| If you change... | Edit first | Then check |
|---|---|---|
| Agent trigger, mode protocol, semantic-injection ambiguity | `skills/llm-gtd/SKILL.md` | `docs/stable-skill.md`, package with `tools/scripts/package_skill.py` |
| Daily GTD behavior, secretary authority, Inbox processing | `vaults/template/AGENTS.md` | Demo vault and component upgrade for `agent_instructions` |
| Dashboard UI/data projection | `vaults/template/Dashboard.html`, `vaults/template/export_dashboard.py` | `tools/setup/components.json` component `dashboard` |
| Online doc lifecycle or remote cleanup | `docs/architecture.md`, `skills/llm-gtd/SKILL.md` | `setup-state` capability `im_docs` |
| IM brief or scheduling-doc behavior | `vaults/template/AGENTS.md`, `vaults/template/05 - Reference/doc-sync-protocol.md` | component `doc_sync_protocol` |
| Setup questions or initial install flow | `tools/setup/init.py` | `docs/setup-guide-for-agent.md`, setup-state fields |
| Component upgrade behavior | `tools/setup/components.json`, `tools/setup/components.py`, `tools/setup/upgrade.py` | `.llm-gtd/component-state.json` semantics |
| Local macOS automation | `tools/setup/create_launchd.py` | `doctor.py`, uninstall behavior |
| Dashboard.app wrapper | `tools/setup/create_app.py`, `tools/resources/*` | component `dashboard_app` |
| QuickCapture | `tools/setup/install_quickcapture.py`, `tools/scripts/quickcapture/*` | component `quickcapture` |
| Safe uninstall | `tools/setup/uninstall.py` | `Skill.md` uninstall protocol, setup-state capability labels |
| Doctor/reporting | `tools/setup/doctor.py` | layer labels in architecture docs |

## Host Reliability Checklist

When changing triggers or capture wording, check both host modes:

- **Workspace-bound:** the Agent is in a GTD vault workspace and can rely on `AGENTS.md` / `CLAUDE.md`.
- **Semantic-injection only:** the Agent only received this skill because the message looked related. Generic phrases such as `记一下` require a clarification unless GTD intent is explicit.

Tests should protect both the presence of the ambiguity rule in `Skill.md` and the daily capture behavior in `AGENTS.md`.

## Render / IM Surface Checklist

When changing any mode, ask whether each surface is affected:

| Surface | Setup | Daily | Doctor | Upgrade | Uninstall |
|---|---|---|---|---|---|
| Dashboard | create files/app | export after vault changes | verify files/jobs | apply dashboard component only | remove local app/jobs only |
| Daily IM brief | connect or pending | overwrite from full vault scan | verify if tools exist | review if protocol changed | disable or mark pending |
| Scheduling doc | connect or pending | update external deliverables only | verify if tools exist | review if protocol changed | disable or mark pending |

`doc_sync_protocol` is a managed component. If that component changes, upgrade should mark `im_docs` for runtime review because local scripts cannot verify or migrate remote online documents by themselves.

If a surface cannot be maintained because tools or credentials are unavailable, record the state as pending/manual rather than pretending it is complete.

## Release Checklist

1. Bump `VERSION` when repo behavior changes.
2. Bump `skills/llm-gtd/SKILL.md` version when Agent mode protocol or activation policy changes.
3. Update `tools/setup/components.json` when adding or moving managed components.
4. Run `python3 -m unittest discover -s tests`.
5. Run `python3 tools/scripts/package_skill.py`.
6. Confirm packaged skill contains the intended version.
