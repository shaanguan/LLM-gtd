#!/usr/bin/env bash
# LLM-GTD iteration observer — run anytime to see release vs local state.
set -euo pipefail

REPO="${LLM_GTD_REPO:-$HOME/LLM-gtd}"
VAULT="${GTD_VAULT:-$HOME/Documents/GTD}"
SKILL="$HOME/.agents/skills/llm-gtd/SKILL.md"
HERMES_LINK="$HOME/.hermes/skills/llm-gtd"

echo "╔══════════════════════════════════════════════╗"
echo "║   LLM-GTD Iteration Status                   ║"
echo "╚══════════════════════════════════════════════╝"
echo

echo "## GitHub (shaanguan/LLM-gtd)"
if command -v gh >/dev/null 2>&1; then
  gh release list --repo shaanguan/LLM-gtd --limit 5 2>/dev/null || echo "  (gh failed — check auth)"
  echo
  echo "  Latest commit on main:"
  gh api "repos/shaanguan/LLM-gtd/commits?per_page=3" \
    --jq '.[] | "  \(.sha[0:7]) \(.commit.message | split("\n")[0])"' 2>/dev/null || true
else
  echo "  Install gh CLI for remote status"
fi
echo

echo "## Factory (repo VERSION)"
if [[ -f "$REPO/VERSION" ]]; then
  echo "  $REPO/VERSION → $(cat "$REPO/VERSION")"
  if [[ -d "$REPO/.git" ]]; then
    echo "  branch: $(git -C "$REPO" branch --show-current 2>/dev/null) @ $(git -C "$REPO" rev-parse --short HEAD 2>/dev/null)"
    git -C "$REPO" status -sb 2>/dev/null | head -1 | sed 's/^/  /'
  fi
else
  echo "  no clone at $REPO"
fi
echo

echo "## Skill (Agent loader)"
if [[ -f "$SKILL" ]]; then
  rg '^version:' "$SKILL" | head -1 | sed 's/^/  /'
  rg 'stable_contract:' "$SKILL" 2>/dev/null | head -1 | sed 's/^/  /' || true
else
  echo "  not installed (~/.agents/skills/llm-gtd)"
fi
if [[ -L "$HERMES_LINK" ]]; then
  echo "  Hermes symlink: OK → $(readlink "$HERMES_LINK")"
elif [[ -e "$HERMES_LINK" ]]; then
  echo "  Hermes: exists (not symlink)"
else
  echo "  Hermes symlink: missing"
fi
echo

echo "## Vault (user state)"
if [[ -d "$VAULT" ]]; then
  echo "  path: $VAULT"
  if [[ -f "$VAULT/.llm-gtd/version" ]]; then
    echo "  product version: $(cat "$VAULT/.llm-gtd/version")"
  fi
  if [[ -f "$VAULT/.llm-gtd/setup-state.json" ]]; then
    python3 - <<PY 2>/dev/null || true
import json, pathlib
p = pathlib.Path("$VAULT/.llm-gtd/setup-state.json")
d = json.loads(p.read_text())
print("  next_step:", d.get("next_step", "?"))
caps = d.get("capabilities", {})
bad = [k for k,v in caps.items() if v in ("pending","error","runtime_cleanup_pending","manual_removal_required")]
if bad:
    print("  attention:", ", ".join(f"{k}={caps[k]}" for k in bad))
PY
  fi
  notes=$(find "$VAULT" -path '*/0[0-7]*' -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  echo "  user notes (00~07): ${notes} md files"
else
  echo "  no vault at $VAULT (clean for fresh setup test)"
fi
echo

echo "## Quick checks"
echo "  npx skills add shaanguan/LLM-gtd --skill llm-gtd -g -y   # align skill to latest release"
echo "  设置 GTD / 升级 GTD                                      # Agent-driven vault changes"
echo "  python3 $REPO/tools/setup/doctor.py --vault \"$VAULT\" --json  # health (when vault exists)"
