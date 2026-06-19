# Writing Guidelines

Use this guide when editing product docs, skill instructions, and Agent-facing playbooks.

## Product Language

Write from ownership first:

```text
Core owns the GTD contract.
Vault holds durable user state.
Providers supply capabilities.
Agent discovers and verifies providers at runtime.
```

Prefer positive contracts over defensive disclaimers:

| Use | Pattern to avoid |
|---|---|
| `Providers supply render, capture, scheduler, messaging, backup, and diagnostic capabilities.` | Defining core by negating named providers. |
| `External surfaces are provider-managed projections.` | Explaining runtime authority as script helplessness. |
| `Uninstall preserves user notes.` | Using danger language for ordinary ownership boundaries. |
| `Report runtime cleanup after provider/tool verification.` | Describing verification as an anti-claim rule. |

## Where Provider Names Belong

Concrete provider names belong in provider docs, compatibility notes, tests, and implementation paths. Core docs should use capability slots first: `render`, `capture`, `scheduler`, `messaging`, `online_docs`, `backup`, `diagnostics`.

When an example helps, introduce it as an example:

```text
Render providers can include a local dashboard, a web view, or an Agent-native panel.
```

## Safety Language

Use hard negatives only for destructive or high-risk actions:

- deleting user data
- reporting external runtime cleanup
- sharing or writing to external systems
- archiving/completing user commitments

For ordinary architecture boundaries, use capability ownership instead of prohibition.

## Tests

Tests should protect the abstraction, not a defensive sentence. Assert terms such as `Capability Providers`, `provider/tool verification`, and `Vault remains the source of truth`; avoid pinning tests to one provider name unless that provider is the feature under test.

## Release Check

Before packaging, scan changed product docs and skill files for negation-based architecture boundaries, provider-specific denial phrases, and conversation residue.

Each match should either be a deliberate safety rule, a compatibility note, or rewritten as a positive ownership statement.
