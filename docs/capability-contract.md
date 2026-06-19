# Capability Contract

LLM-GTD core exposes a small set of capability slots. Agent frameworks, user-installed packages, and bundled examples can attach providers to those slots.

The stable rule is:

```text
Core defines extension points.
Providers supply capabilities.
Agent discovers capabilities at runtime.
Vault remains the source of truth.
```

## Core Responsibilities

Core owns only:

- The GTD vault contract: folders, frontmatter, lifecycle/status semantics, and user-data preservation.
- Agent behavior: capture, clarify, organize, reflect, engage, and evidence-based answers.
- Capability slots: named optional extension points.
- Discovery and degradation rules: use a verified capability when present; otherwise continue with the vault-first workflow and record the capability state.

## Capability Slots

| Slot | Purpose | Example providers |
|---|---|---|
| `capture` | Ingest raw user input into Inbox | Chat, IM gateway, desktop hotkey, import command |
| `render` | Produce user-facing views from vault state | Dashboard, daily brief, status page |
| `scheduler` | Trigger recurring Agent routines | Agent framework scheduler, cron adapter |
| `online_docs` | Publish selected projections to remote documents | Feishu, DingTalk, Google Docs, other doc MCP |
| `messaging` | Send or receive short user-facing messages | IM gateway, mobile Agent, desktop notification |
| `health_check` | Validate vault/tool/runtime state | doctor helper, plugin-specific verifier |
| `backup` | Preserve recoverable history | git snapshot, Time Machine, cloud backup adapter |
| `automation` | Run local or remote repeatable jobs | launchd, workflow runner, hosted automation |

Examples illustrate possible providers; the slot names are the stable contract.

## Discovery Rules

Before using a capability, the Agent should check evidence such as:

- `.llm-gtd/setup-state.json` capability status.
- `.llm-gtd/component-state.json` component status.
- Files that prove a provider exists, such as plugin config or executable files.
- Agent framework tools exposed in the current session.
- Plugin-specific doctor output.

Provider-specific commands run after discovery succeeds. When discovery is inconclusive, record the state and continue with the vault-first workflow.

## Degradation Values

Use capability states instead of binary installed/missing claims:

| State | Meaning |
|---|---|
| `ok` | Capability is present and verified. |
| `skipped` | Capability is not enabled for this vault/session. |
| `pending` | User selected the capability, but setup/runtime work remains. |
| `manual_verify` | Agent cannot verify automatically; user or provider-specific tools must check. |
| `runtime_review_required` | Core changed rules that a runtime provider may need to re-apply. |
| `runtime_cleanup_pending` | Local uninstall ran, but external runtime cleanup still needs provider tools. |
| `error` | Capability was selected but failed verification. |

## Agent Rules

- Use capability language in core instructions: render capability, capture capability, scheduler capability.
- Mention concrete providers as examples, or when the current state proves that provider is enabled.
- Keep setup, daily use, upgrade, doctor, and uninstall functional with no providers attached.
- Report provider changes only after verification through provider evidence.
- Keep vault writes authoritative; provider outputs are projections.

## Plugin Rules

Plugins may be bundled in this repo, installed by a separate package, or injected by an Agent framework. Either way, they should:

- Declare which capability slot they satisfy.
- Store their state in `.llm-gtd/setup-state.json` or a plugin-specific state file.
- Provide a verification path where possible.
- Accept a vault path rather than assuming LLM-GTD-specific paths.
- Be removable without deleting `00 - Inbox` through `07 - Achievements`.
