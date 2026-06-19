# Project Tracks

This open-source repository covers **Personal LLM-GTD** only.

## Project 1: Personal LLM-GTD (this repo)

Goal: make one person's private GTD system reliable, high-agency, and low-friction.

Scope:
- setup and installation reliability
- optional bundled provider examples such as QuickCapture, Dashboard, launchd, and scheduler guides
- personal vault schema
- `AGENTS.md` secretary behavior
- morning / evening / weekly routines
- Inbox clarification quality
- personal Markdown-first trust model

Design anchor:
- [Personal edition design](personal-edition-design.md)

Current priority:
- fix first-run friction
- strengthen high-agency secretary rules
- improve review and prioritization quality
- keep local Markdown as the source of truth

Scope boundary:
- the personal vault remains a private single-user workspace

## Commercial Team Coordination (separate product)

A **closed-source commercial product** may connect to Personal LLM-GTD later for team coordination between private secretaries.

That product, ledger, protocol, and implementation ship separately.

What is public here:
- Personal LLM-GTD is closed-loop on its own
- a future commercial layer would connect through **selective publish / subscribe**
- private vaults stay private; only chosen commitments or status cross the boundary

Separate product scope:
- shared commitment ledger schemas
- secretary-to-secretary protocol details
- audit/event/message implementations
- pricing, licensing, or deployment for the commercial product

If you only need a personal GTD secretary, you can ignore the commercial track entirely.

## Relationship (high level)

```text
Personal LLM-GTD (open source, this repo)
  private vault + private secretary
        |
        | optional future integration
        | publish selected commitment / blocker / status
        | subscribe shared commitment / nudge / evidence
        v
Team coordination product (commercial, separate codebase)
```

Without any commercial integration, Personal LLM-GTD is a complete single-person system.
