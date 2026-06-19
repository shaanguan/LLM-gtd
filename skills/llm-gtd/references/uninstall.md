# Uninstall Playbook

1. Run:

```bash
python3 "$REPO_PATH/tools/setup/uninstall.py" --vault "$VAULT_PATH"
```

2. The script removes selected scriptable local providers. Platform scheduler jobs, messaging gateways/webhooks, online doc credentials, and the installed skill package are handled through their own provider or framework tools.
3. Read `$VAULT_PATH/.llm-gtd/setup-state.json` and, if present, `$VAULT_PATH/.llm-gtd/agent-cron-guide.md`.
4. If scheduler tools are available and that capability was enabled, remove the scheduler jobs. Otherwise report runtime cleanup pending.
5. If messaging/online-doc tools are available and those capabilities were enabled, disconnect or disable runtime integrations. Otherwise report cleanup pending.
6. Remove the installed skill package only if the user explicitly asked to uninstall the skill itself.
7. Confirm that `00 - Inbox` through `07 - Achievements` remain preserved.

## Pitfalls

- Preserve `00~07` because it is user data.
- Scheduler jobs are managed through scheduler tools when that integration was enabled.
- Messaging/doc webhooks and credentials are external runtime; verify changes with actual tools.
