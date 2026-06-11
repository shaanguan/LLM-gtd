# LLM Wiki — Schema

This wiki covers GTD (Getting Things Done) methodology and personal productivity concepts based on David Allen's published work. It serves as a quick-reference knowledge base for the AI agent when making GTD-related decisions.

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

1. Read `wiki/index.md` to find relevant pages.
2. Read relevant wiki pages.
3. Synthesize an answer with wiki-link citations.
4. If the answer is substantial, offer to file it as a new wiki page.

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
5. **Be honest about gaps.** If the wiki doesn't cover something, say so.
