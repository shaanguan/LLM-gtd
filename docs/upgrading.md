# Upgrading LLM-GTD

Personal LLM-GTD upgrades happen in **three layers**. User notes in `00 - Inbox` through `07 - Achievements` are always preserved.

## 1. Upgrade the skill

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
