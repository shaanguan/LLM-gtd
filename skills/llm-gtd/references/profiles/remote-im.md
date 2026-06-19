# Remote IM Profile

Use this profile when the user interacts through IM, mobile, gateway, scheduled jobs, or any semantic skill injection where the GTD vault is not the current workspace. The profile is platform-neutral; the primary current hosts are OpenClaw and Hermes Agent.

## Contract

- Resolve `$VAULT_PATH` before state-bearing work.
- Read `$VAULT_PATH/AGENTS.md` before GTD decisions when the vault is reachable.
- Treat generic capture phrases as ambiguous unless GTD intent is explicit.
- Keep replies short and action-oriented; IM is an operating surface, not a long editing session.
- Report online docs, webhooks, scheduler jobs, or IM credential changes after tool verification.

## Capture

Clear GTD markers include task, todo, deadline, project, next action, waiting-for, review, inbox, `GTD`, `待办`, `项目`, `DDL`, `回顾`.

If markers are present, capture to `00 - Inbox/` and refresh discovered projection providers when tools allow.

If markers are missing, ask one short clarification:

```text
这是要放进 GTD Inbox，还是普通记忆/知识库？
```

If the user chooses GTD, continue with capture. If they choose memory or knowledge, stop GTD handling.

## Runtime Duties

- Scheduler jobs are Agent Runtime. Use available scheduler tools when present; otherwise report `agent_cron: pending` or `runtime_review_required`.
- Online docs and messages are External Surfaces. Verify target identity before writes; otherwise report the capability as pending or cleanup-pending.
- Online docs and messages are projections from the vault. Regenerate from full vault state, not from the current message diff.

## Setup

Ask for messaging or online-doc capabilities as preferences, but keep the profile name platform-neutral. Provider-specific commands belong in setup scripts, generated guides, or connector-specific tools.
