# Architecture

## Overview

GTD Workbench is a three-layer system that turns an Obsidian vault into a fully automated Getting Things Done workflow, driven by an AI agent running inside QoderWork.

```
┌─────────────────────────────────────────────────────────────────┐
│                        RENDER LAYER                              │
│  Dashboard.html │ Daily IM Brief │ Scheduling Doc (DingTalk)    │
└────────────┬───────────────┬──────────────────┬─────────────────┘
             │               │                  │
             │    export_dashboard.py            │  DingTalk MCP
             │               │                  │
┌────────────▼───────────────▼──────────────────▼─────────────────┐
│                        AGENT LAYER                               │
│  QoderWork + AGENTS.md (auto-injected context)                  │
│  • Cron jobs: morning brief, evening review, weekly review      │
│  • On-demand: user conversations, inbox processing              │
│  • Knowledge base: knowledge/gtd/wiki/ (methodology reference)  │
└────────────┬────────────────────────────────────────────────────┘
             │  read / write / move / archive
┌────────────▼────────────────────────────────────────────────────┐
│                       STORAGE LAYER                              │
│  Obsidian Vault ($GTD_VAULT)                                    │
│  ┌──────────┬──────────┬──────────┬──────────┬────────────┐    │
│  │ 00-Inbox │01-Project│02-NA     │03-WF     │04-Someday  │    │
│  ├──────────┼──────────┼──────────┼──────────┼────────────┤    │
│  │05-Ref    │06-Archive│07-Achieve│Templates │Scripts     │    │
│  └──────────┴──────────┴──────────┴──────────┴────────────┘    │
│  + AGENTS.md  + Dashboard.html  + export_dashboard.py           │
│  + .gtd-workbench/ (state: heartbeat, config)                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Capture** — User captures thoughts via Obsidian (manual), Raycast quick-entry, or by telling the agent in chat. All land in `00 - Inbox/`.

2. **Process** — The agent (or user) applies the GTD decision tree (see AGENTS.md §8.1). Items flow to Projects, Next Actions, Waiting For, Someday Maybe, Reference, or Trash.

3. **Organize** — Each NA gets frontmatter: `project`, `due`, `priority`, `okr`, `owner`, `tags`, `requester`. The agent enforces quality (verb-first, physically actionable, startable now).

4. **Review** — Scheduled cron jobs run morning briefs (MIT selection), evening reviews (completion check + inbox sweep), and weekly reviews (full system audit).

5. **Render** — After any vault change, `export_dashboard.py` regenerates Dashboard data. DingTalk documents get block-level updates via MCP.

## Key Design Decisions

**Single environment variable (`$GTD_VAULT`)** — All scripts locate the vault via this one variable. No config file is strictly required; the system works with sensible defaults out of the box.

**AGENTS.md as the brain** — The 17-section operational manual is injected into every agent session. It is the canonical source of truth for behavior, overriding memory. Changes to AGENTS.md take effect immediately.

**Conditional features** — OKR tracking, DingTalk integration, side-project isolation, and knowledge-base references are all optional. The `setup/init.py` renders only the sections you enable.

**Vault is the IDE** — The agent has full write delegation over the vault. The user never needs to manually organize files. The vault's internal structure can evolve freely as long as the export script absorbs the change and the render-layer shape stays stable.

**Render-layer audience separation** — Dashboard shows everything (for the user). DingTalk scheduling doc shows only externally-relevant deliverables (for requesters). Daily brief shows only MIT (for colleagues). Different granularity, same source of truth.

**Knowledge base is repo-level, not per-vault** — The GTD methodology wiki ships with the repo and is shared. Individual vaults reference it via AGENTS.md §8's decision-anchor table. Users can maintain their own private source and sync via `scripts/sync-knowledge.sh`.

## File Responsibilities

| File | Responsibility |
|------|---------------|
| `AGENTS.md` | Agent behavior, rules, permissions, cron flows, methodology anchors |
| `Scripts/_config.py` | Shared config: vault path resolution, defaults, helper functions |
| `Scripts/cron_heartbeat.py` | Track which crons ran; alert on missed beats |
| `Scripts/verify_sync.py` | Frontmatter lint + render-layer drift detection |
| `Scripts/inbox_sla.py` | Alert if Inbox items sit > N hours unprocessed |
| `Scripts/preflight.py` | Pre-cron self-check + PTO on/off toggle |
| `export_dashboard.py` | Scan vault → generate DATA JSON → inject into Dashboard.html |
| `Dashboard.html` | Static HTML dashboard — opens locally via `file://`, no server |
| `setup/init.py` | Interactive initializer — renders template into a vault |
| `setup/doctor.py` | Post-setup health check |
| `scripts/sync-knowledge.sh` | Rsync private knowledge source → `knowledge/gtd/` mirror |

## Security Model

The agent operates under a trust model where the vault owner grants full file-system delegation within `$GTD_VAULT`. The hard red lines (AGENTS.md §5) enforce safety:

- No permanent file deletion (only trash or archive)
- No Dashboard structure changes (only data injection)
- No archiving without user confirmation
- No business-decision substitution

DingTalk operations are further constrained: only specific document blocks can be written, image-bearing blocks are untouchable, and every write is preceded by a nodeId + title verification.
