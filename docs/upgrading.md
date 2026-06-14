# Upgrading LLM-GTD

Personal LLM-GTD upgrades happen in **three layers**. User notes in `00 - Inbox` through `07 - Achievements` are always preserved.

## Design: vault-first, skill-stable

**Default path for users:** say `升级 GTD` / `upgrade gtd` to the Agent. The skill (once installed) should run `setup/upgrade.py` and refresh vault runtime files — no skill reinstall required for most releases.

| Put changes in… | When | User action |
|---|---|---|
| **Vault** (`AGENTS.md`, templates, scripts, guides) | GTD rules, routines, UI, setup scripts | Natural language: `升级 GTD` |
| **Skill** (`skills/llm-gtd/SKILL.md`) | Loader/router only: triggers, upgrade command wiring | Reinstall skill — **rare** |

Maintainership goal: **most releases only bump `VERSION` + vault template**; skill updates only when trigger routing or install plumbing changes. See [Stable skill contract](stable-skill.md).

## Natural-language upgrade (recommended)

User says:

```text
升级 GTD
```

Agent should:

1. `python3 setup/upgrade.py --vault "$GTD_VAULT" --check --json`
2. If update available: `--apply --pull-repo` (or `git pull` + `--apply`)
3. `python3 setup/doctor.py --vault "$GTD_VAULT" --check-updates --check-cron --json`
4. Report what changed; remind that user notes in `00~07` were preserved

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

## 3. Apply vault runtime upgrade

Updates template/runtime files (`AGENTS.md`, `CLAUDE.md`, guides, Dashboard shell, `.llm-gtd/version`). Does **not** overwrite existing markdown inside `00~07` folders.

```bash
git -C /path/to/LLM-gtd pull --ff-only   # if you use a git checkout
python3 setup/upgrade.py --vault "$GTD_VAULT" --apply --pull-repo
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
| `.llm-gtd/version` (vault) | Last applied vault runtime version |

If `.llm-gtd/version` is older than repo `VERSION`, run `setup/upgrade.py --apply`.

## Custom AGENTS.md edits

`upgrade.py` re-renders `AGENTS.md` from the latest template. If you added personal rules directly to `AGENTS.md`, back up first or keep those rules in git inside your vault.

## QuickCapture after non-interactive setup

If QuickCapture was skipped during agent setup:

```bash
python3 setup/install_quickcapture.py --vault "$GTD_VAULT" --repo /path/to/LLM-gtd
```
