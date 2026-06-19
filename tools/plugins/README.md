# Tool Plugins

This directory is the ownership boundary for optional capabilities around a vault.

LLM-GTD core works with the skill, vault contract, and Agent. The compatibility commands in `tools/setup/` remain the public wrappers for now, while implementation ownership gradually moves here.

Current plugin families:

- `dashboard/` — vault visualization and desktop wrapper ownership
- `quickcapture/` — configurable capture entrypoint ownership
- `local-automation/` — launchd and local scheduled refresh/snapshot ownership
- `scheduler/` — Agent scheduler guide/adapter ownership
- `online-docs/` — IM and online document projection ownership
