# Reference

Long-lived reference material that doesn't fit into a project or action.

Use this folder for durable context the Agent should be able to consult later:

- collaborator notes
- operating preferences
- project background
- review conclusions
- reusable checklists
- personal methodology notes

Keep action-bearing work in `01 - Projects/`, `02 - Next Actions/`, or `03 - Waiting For/`. Reference material should explain context, not become a hidden task list.

Optional providers may read reference files when they render views or publish projections, but this folder belongs to the vault contract first.

### `weeks.yaml` (optional)

If present, populates the Weekly card.

```yaml
"6/8–6/12":
  - d: "6/9 Tue"
    items:
      - "Achievement of the day"
      - "Another wrap-up"
"6/1–6/7":
  - d: "6/3 Wed"
    items:
      - "Earlier achievement"
```

Both files are pure data — delete them to hide the corresponding cards.
