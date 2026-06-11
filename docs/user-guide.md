# User Guide

## Prerequisites

Before you begin, make sure you have:

1. **An AI Agent environment** — QoderWork, Claude Desktop, or any tool that supports AGENTS.md context injection
2. **Obsidian** installed (any version)
3. **Python 3.9+** available (for the helper scripts)
4. An IM platform account (optional, for team-facing document sync — DingTalk, Feishu, or WeCom supported)

## Quick Start (5 minutes)

### Step 1: Clone the repo

```bash
git clone https://github.com/shaanguan/LLM-gtd.git
cd LLM-gtd
```

### Step 2: Run the initializer

```bash
python3 setup/init.py
```

The script asks a few questions:
- **Where to create your vault** — e.g. `~/Documents/GTD`
- **IM platform** — DingTalk, Feishu, WeCom, WeChat, or none
- **Which features to enable** — OKR, document sync, side project, knowledge base
- **Cron schedule** — when to run morning brief, evening review, weekly review

It then copies the vault template, renders your personalized `AGENTS.md`, and prints next steps.

### Step 3: Open in Obsidian

Open Obsidian → "Open folder as vault" → select the path you chose in Step 2.

### Step 4: Point your Agent at the vault

Depending on your platform:
- **QoderWork** — select this vault folder as your working directory
- **Claude Desktop** — add the vault path to your project settings
- **Other** — ensure your agent can read/write this directory

The `AGENTS.md` file will be auto-injected into every agent session from now on.

### Step 5: Register cron jobs

Set up scheduled tasks for automated flows:
- **QoderWork** — use the built-in scheduled tasks panel
- **Claude Desktop** — use macOS `launchd` or Linux `crontab` to trigger the agent
- **Other** — trigger manually or set up your own scheduler

Tasks to register:
- Morning brief (e.g. daily 10:30)
- Evening review (e.g. daily 22:30)
- Weekly review (e.g. Sunday 21:00)
- Git snapshot (daily 23:55) — automatic vault backup

### Step 6: Verify

```bash
python3 setup/doctor.py --vault ~/Documents/GTD
```

This runs a health check and reports any issues.

## Daily Workflow

Once set up, your daily flow looks like this:

**Morning** — The agent sends you a brief via IM: today's MITs (max 3), upcoming deadlines, waiting-for status, and one GTD insight from the knowledge base. You glance at it and go.

**Throughout the day** — Capture anything by telling the agent ("add to inbox: call back the vendor about pricing") or dropping a note in `00 - Inbox/` via Obsidian / Raycast.

**Evening** — The agent asks which of today's tasks were completed. Confirmed items get archived to `06 - Archive/` and logged in `07 - Achievements/`. It sweeps Inbox for anything unprocessed, updates the Dashboard, and refreshes shared docs (if enabled).

**Weekly** — A deeper review: walk every list, check for stalled projects, review Someday Maybe for activation, plan next week, and align with OKR progress.

## Customization

### config.yaml (optional)

Create `$GTD_VAULT/.llm-gtd/config.yaml` to override any default. See `setup/config.schema.yaml` for the full reference.

Common overrides:
```yaml
cron_expectations:
  morning: "daily 09:00"    # earlier start
  weekly: "Fri 18:30"       # Friday instead of Sunday

inbox_sla_hours: 2          # stricter inbox processing SLA

dashboard_freshness_hours: 6
```

### IM document sync

After running `init.py` with document sync enabled:
1. Create shared documents on your IM platform (scheduling table + daily brief)
2. Note down their document IDs from the URL
3. Edit your `AGENTS.md` §4 — replace the placeholder IDs with the real ones
4. Grant your agent's IM connector access to those docs

Supported platforms: DingTalk (钉钉), Feishu (飞书). WeCom and WeChat support message push only (no shared documents).

### Adding a side project

If you enable `side_project` during init, a dedicated section appears in AGENTS.md. Side project items:
- Live in `02 - Next Actions/` like everything else
- Are tagged or prefixed to distinguish them
- Never appear in shared docs or work briefs
- Get their own cadence (you set this in AGENTS.md §13)

### Knowledge base

The `knowledge/gtd/` directory ships ~50 wiki pages covering GTD methodology. The agent references these during inbox processing and reviews.

To use your own private knowledge source:
```bash
export GTD_KB_SRC="$HOME/path/to/your/knowledge"
./scripts/sync-knowledge.sh --apply
```

## Updating

When the upstream `llm-gtd` repo gets new features:

```bash
cd llm-gtd && git pull

# Re-run init if the template changed significantly:
python3 setup/init.py --vault ~/Documents/GTD

# Or manually diff your AGENTS.md against the new template:
diff vault-template/AGENTS.md ~/Documents/GTD/AGENTS.md
```

The initializer will not overwrite files that already exist in your vault, so your data is safe.

## Troubleshooting

Run `python3 setup/doctor.py` for automated diagnostics. Common issues:

| Symptom | Fix |
|---------|-----|
| "AGENTS.md has unresolved placeholders" | Re-run `init.py` or manually fill in the `{{...}}` values |
| Dashboard shows stale data | Run `cd $GTD_VAULT && python3 export_dashboard.py` |
| Cron not firing | Check your scheduled tasks setup; ensure vault is set as context directory |
| IM doc sync errors | Rate limit — the agent auto-retries; if persistent, check your IM connector status |
