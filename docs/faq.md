# FAQ

## General

**Q: Do I need to know GTD to use this?**
Not deeply. The system implements GTD for you — the agent handles the methodology. But reading David Allen's "Getting Things Done" (or at least the knowledge-base wiki pages) will help you understand why the system behaves the way it does.

**Q: Can I use this outside Claude Desktop?**
Yes. The system is platform-neutral: any agent that can read `AGENTS.md` and access the vault works. The `llm-gtd` skill explicitly loads vault instructions so you are not locked to workspace auto-injection. Optional capabilities can be injected by the Agent framework or installed as separate providers.

Agents differ in reliability. A workspace-bound session opened on the GTD vault can rely on `AGENTS.md` / `CLAUDE.md`. A semantic-injection-only agent, such as a host that injects the skill because the message looked related, must treat generic phrases like `记一下` as ambiguous unless GTD intent is explicit.

**Q: Is my data stored in the cloud?**
No. Your vault lives entirely on your local filesystem. The agent processes it locally. The only external communication happens if you enable IM document sync (which pushes summaries to shared docs) or if your agent model uses a cloud API.

**Q: Can multiple people share one vault?**
Not recommended. GTD is inherently personal — your Next Actions, contexts, and priorities are yours. For team coordination, use the shared scheduling doc (which exposes only delivery milestones, not your full task list).

## Setup

**Q: I already have an Obsidian vault. Can I add GTD Workbench to it?**
Yes. Run `init.py` pointing at your existing vault. It will create the GTD directories alongside your existing folders and add AGENTS.md. It never overwrites existing files.

**Q: What if I don't use an online-doc or messaging provider?**
No problem. Messaging/document sync is optional and provider-driven. If you choose none, the conditional doc-sync sections in `AGENTS.md` will be removed and the agent won't attempt external projection operations.

**Q: Can I change features after initial setup?**
Yes. Either re-run `init.py` (it won't overwrite your data files) or manually edit the `<!-- IF feature.X -->` blocks in AGENTS.md.

## Daily Use

**Q: What's the difference between Inbox and Next Actions?**
Inbox (`00 - Inbox/`) is raw capture — anything goes in, no thinking required. Next Actions (`02 - Next Actions/`) are processed, concrete, verb-first tasks you've committed to doing. The agent helps you move items from Inbox to the right list.

**Q: Why did the agent ask whether `记一下` means GTD or memory?**
Because some agents do not run inside a fixed GTD workspace. If the host only injected the skill semantically, `记一下` might mean GTD Inbox, long-term memory, or wiki knowledge. Say `加到 GTD...` or mention task/project/deadline/review to make the intent explicit.

**Q: How does the agent decide my MIT (Most Important Tasks)?**
It scans `02 - Next Actions/` for items with `due` today or tomorrow (the T-1 rule: review tasks need a prep day). Maximum 3 MITs. If more qualify, it asks you which to defer.

**Q: Why does the agent keep asking if things are "completed"?**
GTD principle: only the user can declare something done. "Reviewed" or "submitted" doesn't mean finished — maybe there's follow-up. The agent will never auto-archive.

**Q: My render surface isn't updating.**
Render surfaces are optional providers. If you use the bundled Dashboard provider, run `cd "$GTD_VAULT" && python3 export_dashboard.py`. For other providers, run that provider's verify/refresh command.

## Knowledge Base

**Q: Can I add my own methodology pages?**
Yes. Add `.md` files to `vaults/knowledge/gtd/wiki/` following the schema in `vaults/knowledge/gtd/SCHEMA.md`. The wiki calibrates LLM-GTD terminology and preserves durable synthesis; it does not limit the agent to only those pages.

**Q: Are GTD methodology answers limited to the local wiki?**
No. The agent may use general GTD, secretary, planning, and reasoning ability beyond the wiki. The local wiki and `AGENTS.md` override generic advice when they define an LLM-GTD convention, while user-specific facts still must come from the vault.

**Q: What's the difference between vaults/knowledge/gtd/ and 05-Reference/?**
`vaults/knowledge/gtd/` is methodology reference — GTD concepts, techniques, philosophical background. It's shared and version-controlled with the repo.
`05 - Reference/` is personal reference — your OKR, meeting notes, colleague directory, project specs. It's per-vault and contains your data.

## Troubleshooting

**Q: `npx skills add` hangs or times out during install.**
The skills CLI shows an interactive multi-select ("Which agents do you want to install to?") that needs arrow keys, space, and enter. Agent shell tools often cannot drive that UI. Use non-interactive flags:

```bash
npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y
```

Or pin one agent to skip the picker: add `-a hermes-agent` (or `openclaw`, `cursor`, `claude-code`, etc.).

**Q: How do I upgrade an existing installation?**
Three layers: skill, repo/vault runtime, optional providers. See [Upgrading](upgrading.md). Quick path:

```bash
npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y
python3 tools/setup/upgrade.py --vault "$GTD_VAULT" --apply --pull-repo
python3 tools/setup/doctor.py --vault "$GTD_VAULT" --check-updates --json
```

**Q: The agent seems to have "forgotten" a rule I set.**
Rules belong in AGENTS.md, not just in conversation memory. If you established something important, verify it's written into the appropriate section. AGENTS.md is re-injected every session — memory can fade, this file can't.

**Q: Scheduled routines aren't running.**

Scheduling comes from the scheduler or automation providers you enabled:

1. **Bundled local automation example**:
   ```bash
   launchctl list | grep llm-gtd
   python3 tools/setup/create_launchd.py --vault "$GTD_VAULT" --verify
   ```

2. **Agent scheduler provider** (morning brief, evening review, weekly review — if your platform supports it):
   See `.llm-gtd/agent-cron-guide.md` or run:
   ```bash
   python3 tools/setup/agent_cron.py --vault "$GTD_VAULT" --platform generic --json
   ```

Also verify: (1) the `llm-gtd` skill is installed, (2) the agent can read `AGENTS.md`, (3) if the vault-local Scripts plugin is installed, run `python3 Scripts/preflight.py`.

If agent cron is not supported on your platform, use on-demand triggers: `早`, `回顾`, `周回顾`.

**Q: IM document sync is failing.**
Messaging/doc providers often have rate limits. The agent is designed to retry once after a few seconds. If it persists, check the provider connector status and credentials.

**Q: I forgot which file owns a behavior.**
Use [Maintenance map](maintenance-map.md). It routes changes by behavior: trigger policy, GTD secretary rules, provider capabilities, setup, upgrade, uninstall, and local tools.

**Q: I accidentally deleted a file.**
If the agent did it, it should have moved it to `~/.Trash/` (macOS) or the system recycle bin. Check there first. The nightly git snapshot (23:55 cron) also provides a safety net — `git log` and `git checkout` to recover.
