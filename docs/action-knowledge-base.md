# Action Knowledge Base

LLM-GTD should treat the GTD vault as a **compiled, compounding, auditable personal action knowledge base**, not as a pile of task files.

This borrows two useful ideas:

- From LLM-wiki: knowledge should be distilled into maintained artifacts, queried through indexes, audited through logs, and improved over time.
- From open knowledge formats such as OKF: durable operational knowledge should be plain Markdown with structured metadata, readable by humans and usable by agents/tools without locking the user to one runtime.

## What LLM-GTD Absorbs

| Principle | LLM-GTD meaning |
|---|---|
| Compiled layer | Raw input is compiled into Inbox items, projects, next actions, waiting-for items, references, review notes, and durable project context. |
| State compounding | Useful judgments from reviews and queries can be promoted into project pages, `05 - Reference/`, review logs, or methodology notes. |
| Index-first querying | Start from enabled render/index/list views, folder scans, project lists, and frontmatter before opening deep files. |
| Traceable answers | User-specific facts must point back to current vault files, not memory or plausibility. |
| Logs and history | Capture meaningful ingest/query/review/sync decisions in `.llm-gtd/logs/` or review records so later agents can audit why something happened. |
| Health checks | Look for stale tasks, projects without next actions, Waiting For items without owners, Inbox backlog, completed-but-unarchived items, and project/action drift. |
| Human direction, Agent maintenance | The user speaks naturally; the Agent maintains structure, links, logs, checks, and routine cleanup. |

## Boundary Rules

- Methodology pages calibrate language and local convention; model judgment still handles planning, prioritization, and secretary reasoning.
- GTD facts come from current vault evidence: projects, actions, waiting-for items, references, logs, and setup state.
- Durable insights are promoted selectively into the vault or repo knowledge base when they improve future work.
- Provider outputs such as render surfaces, online docs, and messages are regenerated views over vault state.

## Fact / Judgment Boundary

| Type | Source rule |
|---|---|
| GTD facts | Must come from current vault files: projects, actions, waiting-for items, reference files, logs, or setup state. |
| GTD judgment | May use model reasoning, secretary experience, and GTD methodology, constrained by `AGENTS.md` and vault evidence. |
| Local rules | Come from the user's vault `AGENTS.md`, project/reference pages, and setup state. |
| Methodology calibration | Comes from `vaults/knowledge/gtd/` and repo docs when local terminology or product conventions matter. |

## Practical Query Order

For state-bearing work, prefer:

1. Read `AGENTS.md` for runtime rules.
2. Identify the query type: capture, status, prioritization, review, sync, methodology, or maintenance.
3. Use the narrowest index first: enabled render data if installed, folder list, project list, frontmatter, or review log.
4. Open only the relevant project/action/reference files.
5. Answer with evidence paths for facts and clearly label recommendations as judgment.
6. When a durable insight appears, propose a compounding target before writing.

## Compounding Targets

| Insight type | Target |
|---|---|
| Project blocker pattern | Relevant `01 - Projects/` page |
| Collaborator response pattern | `05 - Reference/collaborators.md` or a project page |
| Personal work preference | `05 - Reference/` or review log |
| Weekly review conclusion | `07 - Achievements/` or review record |
| Product/methodology rule | Repo `vaults/knowledge/gtd/`, `AGENTS.md`, or architecture docs |

## OKF-Inspired File Discipline

Where practical, LLM-GTD-managed files should stay:

- Plain Markdown.
- Structured with YAML frontmatter for machine-readable state.
- Linkable through normal Markdown/Obsidian links.
- Versionable in git without hidden database state.
- Usable by multiple agents, skills, and optional tools.

This keeps the vault portable: the user can change Agent frameworks or capability providers without losing the compiled action knowledge.
