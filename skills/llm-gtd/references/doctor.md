# Doctor Playbook

Run health check:

```bash
python3 "$REPO_PATH/tools/setup/doctor.py" --vault "$VAULT_PATH" --check-updates --check-cron --json
```

Report issues by layer:

- **Vault State:** missing files, broken frontmatter, stale AGENTS.md
- **Capability Providers:** selected/injected capture, render, scheduler, messaging, online-doc, backup, automation, and health-check providers
- **Agent Runtime:** cron jobs, IM connections, skill version

Do not treat manual runtime verification as a local script failure.

## Special notes

- `doctor.py --check-cron` reports `agent_cron: "unknown"` → this is normal. It only detects platform native cron (launchd/crontab), not Hermes scheduler. Verify with `hermes cron list` instead.
- AGENTS.md line count warning → consider trimming to ≤400 lines for context sweet spot; move detail to `05 - Reference/`.
