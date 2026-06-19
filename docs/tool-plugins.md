# Capability Providers

LLM-GTD core is the skill plus the GTD vault contract. Tools add capability providers around the vault.

This boundary keeps the product small: users can use LLM-GTD with only a skill, a vault, and an Agent. Extra tools improve specific workflows as optional additions.

A provider may come from the active Agent framework, a separate package, this repo's bundled examples, or a third party.

See [Capability Contract](capability-contract.md) for the stable extension-point model.

## Injection Model

```text
LLM-GTD Core
  defines capability slots
      ↓
Agent runtime / user / plugin package
  injects concrete providers
      ↓
Agent discovers current capabilities
      ↓
Vault remains authoritative
```

Named tools below are current examples of capability providers.

## Plugin Categories

| Capability slot | Example provider | Current repo files | Managed as | Reuse beyond LLM-GTD |
|---|---|---|---:|---|
| `render` | Dashboard visualization | `tools/plugins/dashboard/vault-assets/*`, `tools/setup/create_app.py` | Optional provider | Can visualize other vault-like systems, including knowledge bases |
| `capture` | QuickCapture | `tools/setup/install_quickcapture.py`, `tools/scripts/quickcapture/*` | Optional provider | Can capture into GTD Inbox, knowledge inbox, or another configured destination |
| `automation` | Local automation | `tools/setup/create_launchd.py` | Optional provider | Can schedule any vault refresh or snapshot routine |
| `scheduler` | Agent scheduler adapter | `tools/setup/agent_cron.py` | Optional provider | Host adapter for scheduled Agent work |
| `online_docs` / `messaging` | Online docs / IM | `tools/plugins/online-docs/vault-assets/*` and gateway-specific tooling | Optional provider | Can publish projections from GTD, knowledge, or project vaults |
| `health_check` | Doctor / upgrade helpers | `tools/setup/doctor.py`, `tools/setup/upgrade.py` | Support tooling | Useful for this repo's packaged components |

## Distribution Rule

Tool plugins may be bundled in this repo for convenience, but they should be distributed, injected, and managed as optional capabilities:

- Setup starts with the core contract and adds providers by selection or discovery.
- Uninstall removes selected local providers separately from the GTD vault.
- Plugin state should be capability-based: `ok`, `skipped`, `pending`, `runtime_review_required`, `runtime_cleanup_pending`.
- Plugins work best with a configurable vault destination when the capability can serve more than GTD.
- Core instructions use capability names such as "render capability" or "capture capability"; provider docs can use concrete provider names.

## Current Transition

`tools/setup/init.py --core-only` installs the core contract. The bundled-tools recipe remains available as a convenience provider bundle for users who want a batteries-included local setup.

Future cleanup should split `tools/` into clearer provider packages once the boundaries are stable.
