# Project Tracks

LLM-GTD has one core personal track and can integrate with an optional external team module.

## Project 1: Personal LLM-GTD

Goal: make one person's private GTD system reliable, high-agency, and low-friction.

Scope:
- setup and installation reliability
- QuickCapture, Dashboard, launchd, agent cron
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

Non-goal:
- do not turn the personal vault into a shared team workspace

## Optional External Module: Team Secretary Network

Goal: coordinate multiple people's private secretaries through a shared Markdown-first commitment memory.

Workspace: `/Users/zhoubo/Team-Secretary-Network`

Scope:
- secretary-to-secretary protocol
- shared commitment ledger
- people / secretary identity
- append-only audit events
- disclosure-controlled shared surfaces
- Jira / Linear / GitHub / docs / IM capture as evidence
- multi-secretary versioning

Design anchor lives in the external module workspace, not this personal LLM-GTD repo.

Current priority:
- define shared objects and events
- preserve private-vault boundaries
- design audit narrative: who changed what, when, why, on whose behalf, and based on what evidence

Non-goal:
- do not clone Jira / Linear
- do not expose everyone's private next actions

## Relationship

Personal LLM-GTD is closed-loop without Team Secretary Network.

Team Secretary Network is an optional coordination layer.

When installed or connected, they communicate through selective publish / subscribe:
- personal secretary publishes selected commitments, blockers, or status updates
- team ledger provides shared commitments, evidence, and nudges
- private vault remains private
- shared Markdown artifacts become the durable coordination memory

Without the external module, Personal LLM-GTD behaves as a fully private single-person GTD system.
