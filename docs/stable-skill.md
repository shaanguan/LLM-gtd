# Stable Skill Contract

Personal LLM-GTD uses a **stable skill + evolving vault** split so users can upgrade with natural language (`升级 GTD`) without reinstalling the skill every release.

## Roles

| Artifact | Role | Update frequency |
|---|---|---|
| `skills/llm-gtd/SKILL.md` | Loader: intent routing, path resolution, script dispatch | **Rare** |
| `vault-template/AGENTS.md` | Brain: GTD behavior, authority, routines | **Often** |
| `setup/*.py`, `VERSION` | Install, upgrade, doctor, automation | **Often** |
| `docs/setup-guide-for-agent.md`, `docs/upgrading.md` | Detailed operational reference | **Often** |

## What belongs in the skill (frozen contract v1)

- Broad intent matching (description + short mode table)
- `$VAULT_PATH` / `$REPO_PATH` resolution rules
- **Always read `AGENTS.md`**
- Dispatch table: setup → `init.py`, upgrade → `upgrade.py`, doctor → `doctor.py`, uninstall → `uninstall.py`
- Hard safety rules: preserve `00~07`, `npx skills add -y`, no Qoder APIs

## What must NOT go in the skill

- GTD methodology details (MIT rules, inbox tree, review steps)
- Platform-specific cron CLI examples (belongs in `.llm-gtd/agent-cron-guide.md`)
- Feature flags, IM doc sync, OKR conditionals
- Version-specific release notes

Put those in **vault template** or **repo docs**. Users pick them up via `upgrade.py --apply`.

## When to bump the skill version

Bump `skills/llm-gtd/SKILL.md` version and cut a new `.skill` release only when:

1. Intent routing must change (new top-level mode)
2. Path resolution or clone URL changes
3. Stable contract commands rename (`upgrade.py` → something else)
4. Install plumbing changes (skills CLI flags, package name)

Do **not** bump the skill for AGENTS.md edits, dashboard changes, or setup script improvements — bump repo `VERSION` and let users run vault upgrade.

## User-facing upgrade path

```text
User: 升级 GTD
  → skill (stable) runs upgrade.py
  → vault gets new AGENTS.md + templates
  → user notes in 00~07 untouched
```

Skill reinstall: first install, or when stable contract version changes.

Track contract with frontmatter `stable_contract: 1` in `SKILL.md`. Increment only on breaking loader changes.
