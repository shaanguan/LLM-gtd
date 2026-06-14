# Personal Edition Design

## Positioning

Personal LLM-GTD turns one person's messy work and life inputs into a trusted Markdown-first execution system, operated by a high-agency GTD secretary.

The user should not have to become the system administrator of their own productivity. They should be able to say what is on their mind, and the secretary should capture, clarify, organize, review, and surface the right next moves.

## Product Thesis

The personal edition is not a todo app and not a passive note-taking assistant.

It is:
- a private senior secretary
- a GTD operator
- a trusted external system
- a local Markdown vault with generated surfaces
- a decision-support layer for daily execution

## High-Agency Secretary Model

The personal secretary is expected to exercise judgment.

It should:
- infer intent from messy captures
- split mixed thoughts into concrete open loops
- identify projects, next actions, waiting-for items, and someday ideas
- recommend priorities and sequencing from vault evidence
- surface hidden blockers
- challenge vague or overloaded plans
- propose tradeoffs when the day has too many commitments
- prepare review batches instead of interrogating one item at a time
- reduce manual tracking across chat, docs, IM, and optional external tools

The secretary is not merely a clerk that fills frontmatter. It should feel like a very capable operator who keeps the trusted system alive.

## Authority Boundary

The boundary is not "the agent cannot decide." The boundary is delegated authority plus explicit auditability.

The secretary may decide and act inside routine personal GTD operations:
- capture new inputs into Inbox
- split or rewrite vague captures into clearer candidates
- move clarified items into Projects, Next Actions, Waiting For, Someday, or Reference
- refresh Dashboard and render surfaces
- suggest MITs from due dates, deadlines, blockers, and project state
- flag stale, duplicate, overloaded, or poorly formed work
- prepare drafts for external messages or document updates

The secretary should escalate before:
- declaring something completed
- permanently deleting anything
- accepting or changing a high-stakes external commitment
- exposing private notes to shared surfaces
- making a political or business tradeoff without enough context
- changing the user's standing priorities when evidence is ambiguous

## Markdown-first Trust Model

The personal vault is the source of truth.

Markdown-first matters because:
- the user can inspect every object
- agent behavior can be corrected through `AGENTS.md`
- generated surfaces can be rebuilt from plain files
- Git snapshots can recover history
- the system does not require a proprietary task database to remain useful

Generated views are allowed. Hidden authoritative state is not.

## Personal Versus Team

The personal edition (this open-source repo) optimizes one person's execution system.

Team coordination between multiple private secretaries is a **separate commercial product**, not part of this repository. It is not open source.

Boundary at a high level:

| Personal LLM-GTD (open source) | Team coordination (commercial, separate) |
|---|---|
| private Inbox, Next Actions, MITs | shared commitments and disclosure |
| personal review, Someday, drafts | secretary-to-secretary coordination |
| local vault as source of truth | audit narrative and external evidence views |

The bridge is **selective publish / subscribe**, not a shared personal vault. Implementation details of the commercial product are not documented here.

## Near-term Personal Optimization Track

1. Reduce setup friction.
2. Make non-interactive installs reliable in agent terminals.
3. Improve first-run empty states and onboarding.
4. Make vault path resolution forgiving without hiding where truth lives.
5. Make Hermes / OpenClaw / generic scheduler docs precise.
6. Strengthen AGENTS.md so the secretary has high agency but clear escalation rules.
7. Improve review quality: fewer mechanical lists, more judgment from vault evidence.
