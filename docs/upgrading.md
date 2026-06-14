# Upgrading LLM-GTD

Personal LLM-GTD upgrades are component-level. User notes in `00 - Inbox` through `07 - Achievements` are always preserved.

## Design: vault-first, skill-stable

**Default path for users:** say `升级 GTD` / `upgrade gtd` to the Agent. The skill runs `setup/upgrade.py`, which compares `setup/components.json` against `.llm-gtd/component-state.json` and applies only changed components.

| Put changes in… | When | User action |
|---|---|---|
| **Agent Runtime** (`AGENTS.md`, cron guide) | GTD rules, routines, runtime prompts | Natural language: `升级 GTD` |
| **Computer Tools** (Dashboard.app, launchd, QuickCapture) | Local UI and automation | Component upgrade or targeted repair |
| **Vault managed files** (templates, scripts, Dashboard shell) | Runtime support files around user data | Component upgrade |
| **Repo knowledge** (`knowledge/gtd`) | GTD methodology calibration and durable synthesis | Component hash + vault link refresh; no user-data copy |
| **Skill** (`skills/llm-gtd/SKILL.md`) | Agent-facing loader protocol | Reinstall skill — rare |

Maintainership goal: **most releases only bump `VERSION` + vault template**; skill updates only when trigger routing or install plumbing changes. See [Stable skill contract](stable-skill.md).

## Natural-language upgrade (recommended)

User says:

```text
升级 GTD
```

Agent should:

1. `python3 setup/upgrade.py --vault "$GTD_VAULT" --check --json`
2. If components changed: `--apply --pull-repo` (or `git pull` + `--apply`)
3. Handle `runtime_actions_required` such as cron review or skill reinstall recommendation
4. `python3 setup/doctor.py --vault "$GTD_VAULT" --check-updates --check-cron --json`
5. Report changed components; remind that user notes in `00~07` were preserved

Skill reinstall is needed only when the installed skill is very old and missing Upgrade Mode entirely.

## 1. Upgrade the skill (occasional)

```bash
npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y
```

Or download [`llm-gtd.skill`](https://github.com/shaanguan/LLM-gtd/releases/latest) from GitHub Releases.

## 2. Check for updates

Against your local repo checkout and GitHub latest release:

```bash
python3 setup/upgrade.py --vault "$GTD_VAULT" --check
```

JSON output:

```bash
python3 setup/upgrade.py --vault "$GTD_VAULT" --check --json
```

Doctor can also remind you:

```bash
python3 setup/doctor.py --vault "$GTD_VAULT" --check-updates
```

## 3. Apply component upgrade

Applies only changed managed components. Does **not** overwrite existing markdown inside `00~07` folders.

```bash
git -C /path/to/LLM-gtd pull --ff-only   # if you use a git checkout
python3 setup/upgrade.py --vault "$GTD_VAULT" --apply --pull-repo
```

Targeted repair examples:

```bash
python3 setup/upgrade.py --vault "$GTD_VAULT" --apply --components dashboard_app --force
python3 setup/upgrade.py --vault "$GTD_VAULT" --apply --components agent_instructions
python3 setup/upgrade.py --vault "$GTD_VAULT" --apply --components gtd_knowledge_base
```

Or let the upgrade script pull for you:

```bash
python3 setup/upgrade.py --vault "$GTD_VAULT" --apply --pull-repo
```

## 4. Verify automation

```bash
python3 setup/doctor.py --vault "$GTD_VAULT" --check-cron --check-quickcapture --check-updates --json
python3 setup/create_launchd.py --vault "$GTD_VAULT" --verify
```

Re-register agent cron jobs if needed using `.llm-gtd/agent-cron-guide.md`.

## Version files

| Location | Meaning |
|---|---|
| `VERSION` (repo root) | Current LLM-GTD release version |
| `.llm-gtd/version` (vault) | Last applied repo version |
| `.llm-gtd/component-state.json` (vault) | Last applied source hash for each managed component |
| `.llm-gtd/knowledge-link.txt` (vault) | Pointer to the repo `knowledge/gtd` asset; the knowledge base is not copied into `00~07` user data |

If `.llm-gtd/version` is older than repo `VERSION`, run `setup/upgrade.py --check --json` and apply changed components.

## Custom AGENTS.md edits

When the `agent_instructions` component changes, `upgrade.py` re-renders `AGENTS.md` / `CLAUDE.md` from the latest template and writes backups to `.llm-gtd/backups/`. Keep personal rules in dedicated reference files when possible.

## QuickCapture after setup

If QuickCapture was skipped during setup (default):

```bash
python3 setup/install_quickcapture.py --vault "$GTD_VAULT" --repo /path/to/LLM-gtd
```
