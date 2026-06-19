# Stable Skill Contract

Personal LLM-GTD uses a **stable Agent-facing skill + component-upgraded installed system** split. Users can say `升级 GTD`; the skill runs the component-aware upgrade helper instead of reinstalling the skill for every release.

## Roles

| Artifact | Role | Update frequency |
|---|---|---|
| `skills/llm-gtd/SKILL.md` | Agent action protocol: intent routing, path resolution, script dispatch, post-script runtime obligations | Rare |
| `vaults/template/AGENTS.md` | Secretary handbook: GTD behavior, authority, routines, sync rules | Often |
| `tools/setup/components.json` | Component manifest for upgrade decisions | When managed components change |
| `tools/setup/*.py`, `VERSION` | Factory/Distribution scripts for install, upgrade, doctor, local tools | Often |
| `.llm-gtd/component-state.json` | Per-vault applied component hashes | Written by setup/upgrade |

## What Belongs In Skill.md

- Broad intent matching.
- `$VAULT_PATH` / `$REPO_PATH` resolution rules.
- Always read `AGENTS.md` before GTD work.
- Mode protocols for setup, upgrade, doctor, uninstall, and daily.
- Host reliability rules for workspace-bound vs semantic-injection-only Agents.
- Clear Agent obligations when scripts cannot act: scheduler jobs, IM MCP/Gateway, online docs credentials, installed skill package.
- Hard safety rules: preserve `00~07`, do not claim runtime cleanup without verification, no legacy Qoder APIs.

## What Must Not Go In Skill.md

- GTD methodology details such as MIT rules or inbox decision trees.
- Platform-specific cron command inventories beyond where to read the guide.
- IM document sync protocols.
- Release notes or component implementation detail.

Put those in `vaults/template/AGENTS.md`, `.llm-gtd/agent-cron-guide.md`, `tools/setup/components.json`, and repo docs.

## When To Bump Skill Version

Bump `skills/llm-gtd/SKILL.md` and package a new `.skill` only when:

1. Intent routing changes.
2. Path resolution changes.
3. Mode protocol changes in a way the Agent must know.
4. Activation / ambiguity policy changes for semantic-injection-only hosts.
5. Stable command names or install plumbing changes.

Do not bump the skill for ordinary AGENTS, Dashboard, template, or local tool changes. Those are component upgrades.

## User-Facing Upgrade Path

```text
User: 升级 GTD
  -> skill resolves vault/repo
  -> upgrade.py --check --json returns changed components
  -> upgrade.py --apply applies only changed components
  -> Agent handles runtime_actions_required if any
  -> user notes in 00~07 are preserved
```

Skill reinstall is needed only for first install or when the `skill_loader` component changes and the user wants the installed loader updated.
