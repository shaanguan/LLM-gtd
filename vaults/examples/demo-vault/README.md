# Demo Vault — Designer "Li Wei"

This is a fictional demo vault showing how GTD Workbench looks in practice.

**Persona:** Li Wei, a UX designer at a mid-size tech company. They work on a mobile app redesign, handle cross-functional design requests, and maintain a personal side project (an open-source icon set).

**What to notice:**
- Frontmatter on every file: `project`, `due`, `priority`, `okr`, `owner`, `tags`
- Inbox items are raw captures (no processing yet)
- NAs are verb-first and physically actionable
- WF items have an `owner` field
- The AGENTS.md is a fully rendered version (no placeholders)

**How to try it:**
```bash
export GTD_VAULT="$(pwd)/examples/demo-vault"
python3 Scripts/preflight.py
python3 export_dashboard.py
open Dashboard.html
```
