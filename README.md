# gtd-workbench

> An AI GTD secretary that lives inside QoderWork.
> Status: **Phase 1 scaffold** — see `docs/` (work in progress).

A reference implementation of a Getting Things Done workflow built on:

- **QoderWork** — agent runtime, AGENTS.md, cron, MCP integrations
- **Obsidian vault** — your single source of truth (Markdown + frontmatter)
- **Dashboard.html** — local zero-server static dashboard rendered from the vault
- **DingTalk** — IM channel for daily/weekly briefings (optional)

## What's here today

```
gtd-workbench/
├── LICENSE                 — MIT
├── README.md               — this file
├── setup/
│   ├── config.schema.yaml  — full config reference + defaults
│   ├── init.py             — interactive initializer (renders template → vault)
│   └── doctor.py           — post-setup health check
├── vault-template/         — copy this into a new vault to bootstrap
│   ├── AGENTS.md           — 17-section template (conditionally rendered)
│   ├── 00 - Inbox/         — capture-everything dropbox
│   ├── 01 - Projects/
│   ├── 02 - Next Actions/
│   ├── 03 - Waiting For/
│   ├── 04 - Someday Maybe/
│   ├── 05 - Reference/
│   │   ├── OKR.md          — paste your objectives here
│   │   └── collaborators.md — three-tier colleague directory
│   ├── 06 - Archive/
│   ├── 07 - Achievements/
│   ├── Templates/          — Action.md / Inbox.md / Project.md
│   ├── Scripts/
│   │   ├── _config.py      — shared config loader ($GTD_VAULT)
│   │   ├── cron_heartbeat.py
│   │   ├── inbox_sla.py
│   │   ├── preflight.py
│   │   └── verify_sync.py
│   ├── Dashboard.html      — empty skeleton, populated by export_dashboard.py
│   ├── export_dashboard.py — vault → Dashboard data sync
│   └── .gitignore
├── knowledge/
│   └── gtd/                — GTD methodology wiki (shared, not per-vault)
│       ├── SCHEMA.md       — wiki conventions & frontmatter spec
│       └── wiki/           — ~50 distilled GTD concept pages
├── scripts/
│   └── sync-knowledge.sh   — pull private KB source → knowledge/gtd/ mirror
├── docs/
│   ├── architecture.md     — three-layer system design
│   ├── user-guide.md       — setup + daily workflow + customization
│   └── faq.md              — common questions answered
└── examples/
    └── demo-vault/         — fictional "Li Wei" walkthrough
```

## Quick Start

```bash
# Clone the repo
git clone https://github.com/<your-org>/gtd-workbench.git
cd gtd-workbench

# Run the interactive initializer
python3 setup/init.py

# It will ask:
#   1. Where to create your vault (e.g. ~/Documents/GTD)
#   2. Which features to enable (OKR, DingTalk, side project, knowledge base)
#   3. Cron schedule (morning/evening/weekly times)
#
# Then it renders AGENTS.md, copies the template, and prints next steps.

# Verify your setup
python3 setup/doctor.py --vault ~/Documents/GTD
```

## AGENTS.md

The `vault-template/AGENTS.md` is the brain of this system — a 17-section operational manual that gets auto-injected into every QoderWork agent session and cron run. It uses `{{placeholder}}` variables and `<!-- IF feature.X -->` conditional sections so that `setup/init.py` can render a personalized copy for each user.

Key sections: identity, three-layer architecture, vault structure, DingTalk ops (optional), hard/soft red lines, permissions, GTD decision anchors with knowledge-base cross-references, behavior code, cron flows, OKR (optional), collaborators, side projects (optional), Dashboard sync, failure defenses, lessons learned, and knowledge base pointers.

## Knowledge Base

The `knowledge/gtd/` directory contains a structured wiki of GTD methodology — distilled concept pages that the agent references during inbox processing, weekly reviews, and morning briefs. It is **not** per-vault; it ships with the repo and is shared across all users.

If you maintain your own private GTD knowledge source, use `scripts/sync-knowledge.sh` to mirror it:

```bash
export GTD_KB_SRC="$HOME/Documents/my-gtd-knowledge"
./scripts/sync-knowledge.sh           # dry-run preview
./scripts/sync-knowledge.sh --apply   # write changes
git diff knowledge/gtd/               # review
git add knowledge/gtd/ && git commit -m "sync(kb): refresh"
```

The AGENTS.md template's §8 "Decision Anchors" section maps common GTD situations to specific wiki pages, so the agent knows exactly which file to `read` first — no full-directory grep needed in the common case.

## Roadmap (from the open-source plan)

- [x] **Phase 1** — repo scaffold + config-ized scripts + Dashboard skeleton
- [x] **Phase 2** — `AGENTS.md` template + knowledge base + decision anchor table
- [x] **Phase 3** — `setup/init.py` interactive bootstrap + `setup/doctor.py` self-check
- [x] **Phase 4** — full docs (`docs/architecture.md`, user guide, FAQ)
- [x] **Phase 5** — `examples/demo-vault/` walkthrough (fictional designer "Li Wei")
- [x] **Phase 6** — release-ready (security audit passed, no personal data)

## License

MIT — see [LICENSE](LICENSE).
