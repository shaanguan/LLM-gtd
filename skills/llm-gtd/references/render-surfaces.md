# Projection Capability Duties

Projection capabilities are the UX view of the same system. They cut across all modes, and providers are discovered at runtime.

Discover `render`, `messaging`, and `online_docs` capabilities before using provider-specific commands.

| Projection | Audience | Purpose | Content rule |
|---|---|---|---|
| Personal render surface | user (self) | GTD command center | Full: every NA/WF/state |
| Daily brief | user + selected recipients | Today's focus | MIT + tomorrow + history |
| Scheduling doc | user + requesters | Requests queued | Only independent delivery milestones |
| Message | user | Fast capture/review loop | Short, vault-backed confirmation |

Core principles:
- The vault has two writers (user manual capture + agent); the render layer must reflect the **current full state** of the vault, not "what I just did this turn".
- Sync = read full vault → emit, **not** "replay this turn's edits".
- Vault changes → refresh all discovered projections together.
- Always regenerate render surfaces from a full vault scan, not just this turn's edits.

Online docs and messages are external projections from vault state. Verify target identity before writes and update according to `05 - Reference/doc-sync-protocol.md` when that file exists.

## Mode responsibilities

| Mode | Personal render | Daily brief / messaging | Scheduling doc |
|---|---|---|---|
| setup | Configure only if a render provider is selected or injected. | Configure only if messaging tools and credentials exist; otherwise mark skipped/pending. | Same as daily brief. |
| daily | After vault changes, refresh only if a render provider is discovered. | If enabled, full-scan vault and overwrite today's brief. | If enabled, full-scan vault and update externally relevant deliverables. |
| doctor | Verify discovered render providers only. | Verify configured targets when tools exist. | Same. |
| upgrade | Apply changed render-provider components only when enabled or explicitly selected. | If agent_instructions or doc_sync_protocol changed, review projection rules. | Same. |
| uninstall | Local script can remove selected local providers only. | Agent must disable remote runtime if tools exist; else report cleanup pending. | Same. |

## In-conversation sync checklist

Run before turn end if vault was touched:

1. Discover enabled projection capabilities from setup state, component state, files, or current Agent tools.
2. Refresh every verified provider from a full vault scan.
3. Skip absent providers without error.
4. Audit: do outputs include items user may have captured outside this turn? (Always read full state, never just push diff.)
