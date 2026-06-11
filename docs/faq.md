# FAQ

## General

**Q: Do I need to know GTD to use this?**
Not deeply. The system implements GTD for you — the agent handles the methodology. But reading David Allen's "Getting Things Done" (or at least the knowledge-base wiki pages) will help you understand why the system behaves the way it does.

**Q: Can I use this without QoderWork?**
Yes! The system works with any AI agent that can read AGENTS.md as context. QoderWork has the best integration (built-in cron, IM connectors), but Claude Desktop, Cursor, or any MCP-compatible agent can run the core workflow. You just need to set up cron externally (launchd / crontab) for automated flows.

**Q: Is my data stored in the cloud?**
No. Your vault lives entirely on your local filesystem. The agent processes it locally. The only external communication happens if you enable IM document sync (which pushes summaries to shared docs) or if your agent model uses a cloud API.

**Q: Can multiple people share one vault?**
Not recommended. GTD is inherently personal — your Next Actions, contexts, and priorities are yours. For team coordination, use the shared scheduling doc (which exposes only delivery milestones, not your full task list).

## Setup

**Q: I already have an Obsidian vault. Can I add GTD Workbench to it?**
Yes. Run `init.py` pointing at your existing vault. It will create the GTD directories alongside your existing folders and add AGENTS.md. It never overwrites existing files.

**Q: What if I don't use DingTalk?**
No problem. During `init.py` setup, choose your preferred IM platform (Feishu, WeCom, WeChat) or select none. If you choose none, the conditional doc-sync sections in AGENTS.md will be removed and the agent won't attempt any IM operations.

**Q: Can I change features after initial setup?**
Yes. Either re-run `init.py` (it won't overwrite your data files) or manually edit the `<!-- IF feature.X -->` blocks in AGENTS.md.

## Daily Use

**Q: What's the difference between Inbox and Next Actions?**
Inbox (`00 - Inbox/`) is raw capture — anything goes in, no thinking required. Next Actions (`02 - Next Actions/`) are processed, concrete, verb-first tasks you've committed to doing. The agent helps you move items from Inbox to the right list.

**Q: How does the agent decide my MIT (Most Important Tasks)?**
It scans `02 - Next Actions/` for items with `due` today or tomorrow (the T-1 rule: review tasks need a prep day). Maximum 3 MITs. If more qualify, it asks you which to defer.

**Q: Why does the agent keep asking if things are "completed"?**
GTD principle: only the user can declare something done. "Reviewed" or "submitted" doesn't mean finished — maybe there's follow-up. The agent will never auto-archive.

**Q: The Dashboard isn't updating.**
Run `cd $GTD_VAULT && python3 export_dashboard.py`. If it still looks stale, hard-refresh the browser (Cmd+Shift+R). The dashboard auto-refreshes on window focus after 5 minutes of inactivity.

## Knowledge Base

**Q: Can I add my own methodology pages?**
Yes. Add `.md` files to `knowledge/gtd/wiki/` following the schema in `knowledge/gtd/SCHEMA.md`. Then reference them in AGENTS.md §8.6's anchor table so the agent knows when to consult them.

**Q: What's the difference between knowledge/gtd/ and 05-Reference/?**
`knowledge/gtd/` is methodology reference — GTD concepts, techniques, philosophical background. It's shared and version-controlled with the repo.
`05 - Reference/` is personal reference — your OKR, meeting notes, colleague directory, project specs. It's per-vault and contains your data.

## Troubleshooting

**Q: The agent seems to have "forgotten" a rule I set.**
Rules belong in AGENTS.md, not just in conversation memory. If you established something important, verify it's written into the appropriate section. AGENTS.md is re-injected every session — memory can fade, this file can't.

**Q: Cron jobs aren't running.**
Check: (1) your agent environment is running, (2) scheduled tasks are registered (QoderWork panel / launchd / crontab), (3) `contextDirs` points to your vault, (4) run `python3 Scripts/preflight.py` to verify the environment is healthy.

**Q: IM document sync is failing.**
IM APIs have rate limits. The agent is designed to retry once after a few seconds. If it persists, check your IM connector status. For DingTalk, ensure you haven't exceeded 8 API calls per cron cycle.

**Q: I accidentally deleted a file.**
If the agent did it, it should have moved it to `~/.Trash/` (macOS) or the system recycle bin. Check there first. The nightly git snapshot (23:55 cron) also provides a safety net — `git log` and `git checkout` to recover.
