# FAQ

## General

**Q: Do I need to know GTD to use this?**
Not deeply. The system implements GTD for you — the agent handles the methodology. But reading David Allen's "Getting Things Done" (or at least the knowledge-base wiki pages) will help you understand why the system behaves the way it does.

**Q: Can I use this outside Claude Desktop?**
Yes. The system is platform-neutral: any agent that can read `AGENTS.md` and access the vault works. The `llm-gtd` skill explicitly loads vault instructions so you are not locked to workspace auto-injection. On macOS, `init.py` installs launchd jobs for local automation.

**Q: Is my data stored in the cloud?**
No. Your vault lives entirely on your local filesystem. The agent processes it locally. The only external communication happens if you enable IM document sync (which pushes summaries to shared docs) or if your agent model uses a cloud API.

**Q: Can multiple people share one vault?**
Not recommended. GTD is inherently personal — your Next Actions, contexts, and priorities are yours. For team coordination, use the shared scheduling doc (which exposes only delivery milestones, not your full task list).

## Setup

**Q: I already have an Obsidian vault. Can I add GTD Workbench to it?**
Yes. Run `init.py` pointing at your existing vault. It will create the GTD directories alongside your existing folders and add AGENTS.md. It never overwrites existing files.

**Q: What if I don't use Feishu?**
No problem. Feishu is the default recommendation, but setup also supports DingTalk, WeCom, WeChat, or none. If you choose none, the conditional doc-sync sections in `AGENTS.md` will be removed and the agent won't attempt IM operations.

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
Run `cd "$GTD_VAULT" && python3 export_dashboard.py`, or run `python3 export_dashboard.py` from the vault root. If it still looks stale, hard-refresh the browser (Cmd+Shift+R). The dashboard auto-refreshes on window focus after 5 minutes of inactivity.

## Knowledge Base

**Q: Can I add my own methodology pages?**
Yes. Add `.md` files to `knowledge/gtd/wiki/` following the schema in `knowledge/gtd/SCHEMA.md`. Then reference them in AGENTS.md §8.6's anchor table so the agent knows when to consult them.

**Q: What's the difference between knowledge/gtd/ and 05-Reference/?**
`knowledge/gtd/` is methodology reference — GTD concepts, techniques, philosophical background. It's shared and version-controlled with the repo.
`05 - Reference/` is personal reference — your OKR, meeting notes, colleague directory, project specs. It's per-vault and contains your data.

## Troubleshooting

**Q: `npx skills add` hangs or times out during install.**
The skills CLI shows an interactive multi-select ("Which agents do you want to install to?") that needs arrow keys, space, and enter. Agent shell tools often cannot drive that UI. Use non-interactive flags:

```bash
npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y
```

Or pin one agent to skip the picker: add `-a hermes-agent` (or `openclaw`, `cursor`, `claude-code`, etc.).

**Q: The agent seems to have "forgotten" a rule I set.**
Rules belong in AGENTS.md, not just in conversation memory. If you established something important, verify it's written into the appropriate section. AGENTS.md is re-injected every session — memory can fade, this file can't.

**Q: Cron jobs aren't running.**

LLM-GTD has two automation layers — check both:

1. **Local launchd** (Dashboard refresh, git snapshot):
   ```bash
   launchctl list | grep llm-gtd
   python3 setup/create_launchd.py --vault "$GTD_VAULT" --verify
   ```

2. **Agent cron** (morning brief, evening review, weekly review — if your platform supports it):
   See `.llm-gtd/agent-cron-guide.md` or run:
   ```bash
   python3 setup/agent_cron.py --vault "$GTD_VAULT" --platform generic --json
   ```

Also verify: (1) the `llm-gtd` skill is installed, (2) the agent can read `AGENTS.md`, (3) run `python3 Scripts/preflight.py`.

If agent cron is not supported on your platform, use on-demand triggers: `早`, `回顾`, `周回顾`.

**Q: IM document sync is failing.**
IM APIs have rate limits. The agent is designed to retry once after a few seconds. If it persists, check your IM connector status. For Feishu/DingTalk, ensure the MCP connector is authenticated and within API limits.

**Q: I accidentally deleted a file.**
If the agent did it, it should have moved it to `~/.Trash/` (macOS) or the system recycle bin. Check there first. The nightly git snapshot (23:55 cron) also provides a safety net — `git log` and `git checkout` to recover.
