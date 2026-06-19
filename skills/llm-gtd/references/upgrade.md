# Upgrade Playbook

1. Run:

```bash
python3 "$REPO_PATH/tools/setup/upgrade.py" --vault "$VAULT_PATH" --check --json
```

2. Inspect `components`, `skill_reinstall_recommended`, and `runtime_actions_required`.
3. Apply changed components only:

```bash
python3 "$REPO_PATH/tools/setup/upgrade.py" --vault "$VAULT_PATH" --apply --pull-repo
```

4. For targeted repair, use:

```bash
python3 "$REPO_PATH/tools/setup/upgrade.py" --vault "$VAULT_PATH" --apply --components dashboard_app --force
```

5. After apply, read `$VAULT_PATH/AGENTS.md`; read `$VAULT_PATH/.llm-gtd/agent-cron-guide.md` only if it exists or `agent_cron_guide` changed.
6. If scheduler-facing guidance changed, review or re-register routines only when a scheduler provider is enabled. If tools are unavailable, report runtime review required.
7. If `skill_loader` changed, recommend `npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y`; run it only when the user wants the loader itself updated.

## Pitfalls

- **Bundled capture provider 异常** → 用户启用了该 provider 时，跑对应 provider repair 命令
- **卸载 scheduler 残留** → uninstall.py 只清本地脚本化 provider，远程/平台 scheduler job 需用对应工具删除
- **Skill/Vault 版本分离** → Skill 升级后 vault 可能滞后，必须 `--check` 对齐
- init.py 默认 core-only，不安装 provider；用户选择 bundled provider 后再跑对应安装器
