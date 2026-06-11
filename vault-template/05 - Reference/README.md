# Reference

Long-lived reference material that doesn't fit into a project or action.

## Optional config files read by export_dashboard.py

### `okr.yaml` (optional)

If present, populates the OKR card on the Dashboard.

```yaml
labels:
  O1: First objective
  O1-KR1: A measurable key result
  O1-KR2: Another key result
  O2: Second objective
colors:
  O1: var(--blue)
  O2: var(--purple)
milestone: 2026-12-31   # optional countdown date in the header
```

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
