# LLM Wiki — Schema

This wiki covers GTD (Getting Things Done) methodology and personal productivity concepts based on David Allen's published work. It serves as a calibration and compounding layer for the AI agent when making GTD-related decisions.

The wiki is not the agent's ability ceiling. The agent may use general GTD, secretary, planning, and reasoning ability beyond these pages. Local wiki pages matter because they preserve the system's terminology, cross-links, prior synthesis, and explicit overrides.

## Directory Structure

```
.
├── SCHEMA.md          # This file. The schema and rules.
└── wiki/              # Concept pages maintained by the LLM.
    ├── index.md       # Content catalog of all wiki pages.
    └── ...            # Concept pages, methodology references, etc.
```

## Layers

**The wiki** (`wiki/`): LLM-maintained markdown files covering core GTD concepts. The LLM owns this layer — creates pages, updates them, maintains cross-references, and keeps everything consistent.

**The schema** (`SCHEMA.md`): This file. Tells the LLM how the wiki is structured and what workflows to follow.

## Page Conventions

### Frontmatter

Every wiki page should have YAML frontmatter:

```yaml
---
type: concept
created: YYYY-MM-DD
tags:
  - tag1
  - tag2
---
```

### Page Types

- **concept**: A page about a GTD idea, technique, or framework (e.g., Weekly Review, Next Action, Context Labels).
- **meta**: Overview pages, index, reading lists.

### Linking

Use Obsidian-compatible wiki-links: `[[filename|显示文字]]`（显示文字可选时用 `[[filename]]`）。Obsidian graph view relies on this format. Do NOT use `[text](file.md)` — the graph won't recognize it.

### File Naming

Use lowercase kebab-case: `gtd-five-steps.md`, `weekly-review.md`, `next-action.md`.

## Domain-Specific Tags

Core GTD tags: `gtd`, `weekly-review`, `inbox-zero`, `next-action`, `context-lists`, `capture`, `clarify`, `organize`, `reflect`, `engage`
Practice tags: `time-management`, `productivity`, `goal-setting`, `project-planning`

## Operations

### Query

When the user asks a GTD-related question:

1. If the question is about the user's actual tasks, projects, due dates, owners, priorities, or completion state, answer from the user's vault evidence, not this wiki.
2. If the question is about GTD methodology, use model judgment and consult `wiki/index.md` when local terminology, prior synthesis, or a cited local page would improve the answer.
3. If a local wiki page conflicts with generic model knowledge, treat the local page as the LLM-GTD convention and explain the distinction when useful.
4. If the answer is substantial and durable, offer to file it as a project note, `05 - Reference/` note, or wiki update. Do not write it automatically.

### Lint

Periodically check for:

1. Contradictions between pages.
2. Orphan pages with no inbound links.
3. Concepts mentioned but lacking their own page.
4. Missing cross-references.

## Principles

1. **The wiki is the product.** Every interaction should leave it richer.
2. **Link liberally.** Cross-references are the wiki's most valuable feature.
3. **Flag contradictions.** Note disagreements explicitly.
4. **Compound knowledge.** Good query answers should become wiki pages.
5. **Be honest about gaps.** If the wiki doesn't cover something, say so, then use model judgment if the user asked for advice rather than a vault fact.
