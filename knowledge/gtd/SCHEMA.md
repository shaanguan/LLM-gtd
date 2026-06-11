# LLM Wiki — Schema

This wiki tracks GTD (Getting Things Done) methodology, time management practices, and related personal productivity knowledge from mifengtd.cn (褪墨・时间管理).

## Directory Structure

```
.
├── SCHEMA.md          # This file. The schema and rules.
├── raw/               # Immutable source documents from mifengtd.cn.
│   ├── assets/        # Images and other media files.
│   └── ...            # Articles about GTD, ZTD, time management, etc.
└── wiki/              # LLM-generated and maintained wiki pages.
    ├── index.md       # Content catalog of all wiki pages.
    ├── log.md         # Chronological record of all operations.
    └── ...            # Entity pages, concept pages, summaries, etc.
```

## Layers

**Raw sources** (`raw/`): Articles from mifengtd.cn covering GTD methodology, ZTD (Zen to Done), time management practices, productivity tools, and habit formation. Immutable — the LLM reads but never modifies.

**The wiki** (`wiki/`): LLM-generated markdown files. The LLM owns this layer — creates pages, updates them, maintains cross-references, and keeps everything consistent.

**The schema** (`SCHEMA.md`): This file. Tells the LLM how the wiki is structured and what workflows to follow.

## Page Conventions

### Frontmatter

Every wiki page should have YAML frontmatter:

```yaml
---
title: Page Title
type: summary | entity | concept | comparison | analysis | meta
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - raw/source-filename.md
tags:
  - tag1
  - tag2
---
```

### Page Types

- **summary**: A summary of a single source article.
- **entity**: A page about a specific person (David Allen, Leo Babauta), organization, product (OmniFocus, ThinkingRock), or project.
- **concept**: A page about a GTD idea, technique, or framework (e.g., Inbox Zero, Weekly Review, Next Action, Context Lists, ZTD Habits).
- **comparison**: A structured comparison between tools, methods, or approaches.
- **analysis**: A synthesized analysis, often born from a query.
- **meta**: Overview pages, reading lists, open questions.

### Linking

Use Obsidian-compatible wiki-links: `[[filename|显示文字]]`（显示文字可选时用 `[[filename]]`）。这样 Obsidian 关系图谱可以正确识别连接。**禁止**使用 `[text](file.md)` 格式——图谱不识别。

### File Naming

Use lowercase kebab-case: `gtd-five-steps.md`, `david-allen.md`, `weekly-review.md`.

## Domain-Specific Tags

Core GTD tags: `gtd`, `ztd`, `weekly-review`, `inbox-zero`, `next-action`, `context-lists`, `capture`, `process`, `organize`, `review`, `do`
Tool tags: `omnifocus`, `thinkingrock`, `doit-im`, `worktile`, `remember-the-milk`, `hipsterpda`
Practice tags: `time-management`, `habit-formation`, `self-discipline`, `goal-setting`, `productivity`
Source tags: `mifengtd`, `zenhabits`, `david-allen`, `book-summary`

## Operations

### Ingest

When a new source is added to `raw/`:

1. Read the source document thoroughly.
2. Create a summary page in `wiki/` (type: summary).
3. Update or create entity pages for prominent people, organizations, products.
4. Update or create concept pages for key ideas, techniques, frameworks.
5. Add cross-references between new and existing pages.
6. Update `wiki/index.md`.
7. Append an entry to `wiki/log.md`.

### Query

When the user asks a question:

1. Read `wiki/index.md` to find relevant pages.
2. Read relevant wiki pages.
3. If needed, consult raw sources for details.
4. Synthesize an answer with citations.
5. If the answer is substantial, offer to file it as a new wiki page.
6. Append a query entry to `wiki/log.md`.

### Lint

Periodically check for:

1. Contradictions between pages.
2. Stale claims superseded by newer sources.
3. Orphan pages with no inbound links.
4. Concepts mentioned but lacking their own page.
5. Missing cross-references.
6. Data gaps that could use more sources.
7. New questions to investigate.

## Principles

1. **The wiki is the product.** Every interaction should leave it richer.
2. **Link liberally.** Cross-references are the wiki's most valuable feature.
3. **Cite sources.** Every factual claim should trace back to a raw source.
4. **Flag contradictions.** Note disagreements explicitly.
5. **Compound knowledge.** Good query answers should become wiki pages.
6. **Stay current.** Update wiki pages when new sources provide updated info.
7. **Be honest about gaps.** If the wiki doesn't cover something, say so.
