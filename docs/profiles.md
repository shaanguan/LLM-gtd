# Interface Profiles

LLM-GTD has one product model and two primary ways to use it. These are interface profiles, not platform names.

```text
Skill = Agent behavior
Vault = durable GTD source of truth
Providers = optional local/remote capabilities

Profile = how the user reaches the skill
```

## Profiles

| Profile | Best for | Agent evidence | Default posture |
|---|---|---|---|
| `remote-im` | Mobile capture, messaging requests, scheduled briefs, online document operations; primary current hosts are OpenClaw and Hermes Agent | Lower: vault path, providers, and credentials may need discovery | Conservative: clarify ambiguous capture and verify remote actions |
| `desktop-workspace` | Deep review, Inbox sweep, batch organization, local provider verification, and vault maintenance | Higher: vault files and `AGENTS.md` are directly readable | Direct: operate from full-vault evidence and discover local providers |

## Remote IM

Use `remote-im` when the user talks through IM, mobile, gateway, scheduled agent jobs, or semantic skill injection. The profile name stays platform-neutral, but the primary current hosts are OpenClaw and Hermes Agent.

Rules:

- Resolve the vault path before writing.
- Ask before capturing generic `记一下` / `帮我记` messages unless GTD intent is explicit.
- Keep replies short and operational.
- Treat online docs, IM messages, webhooks, credentials, and scheduler jobs as external runtime. Report changes after provider/tool verification.

## Desktop Workspace

Use `desktop-workspace` when the GTD vault is opened as the Agent workspace, or when the Agent can directly read `AGENTS.md` / `CLAUDE.md` and the vault folders.

Rules:

- Read workspace instructions first.
- Use full-vault evidence for status, review, planning, and cleanup.
- Prefer batch organization when the user asks for review or sweep.
- Verify local providers with scripts, but still treat remote scheduler and messaging cleanup as provider-dependent.

## Why Profiles Are Platform-Neutral

Providers can change: IM may be Feishu, DingTalk, Telegram, WeCom, WeChat, or another gateway. Desktop Agents may be different applications. The profile should describe the interaction shape, not the vendor.
