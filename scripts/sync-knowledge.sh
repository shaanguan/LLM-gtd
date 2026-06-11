#!/usr/bin/env bash
# sync-knowledge.sh — pull your private GTD knowledge base into the repo mirror.
#
# Usage:
#   GTD_KB_SRC=~/Documents/GTD知识库 ./scripts/sync-knowledge.sh        # dry-run preview
#   GTD_KB_SRC=~/Documents/GTD知识库 ./scripts/sync-knowledge.sh --apply  # actually write
#
# After --apply, run `git diff knowledge/gtd/` to review, then commit.
#
# What it copies:
#   $GTD_KB_SRC/SCHEMA.md            -> knowledge/gtd/SCHEMA.md
#   $GTD_KB_SRC/wiki/                -> knowledge/gtd/wiki/  (deleted-on-source files removed in mirror)
#
# What it skips:
#   raw/             — original scraped sources, kept private
#   .obsidian/       — editor state
#   .DS_Store, *.tmp — OS noise

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${REPO_ROOT}/knowledge/gtd"

if [[ -z "${GTD_KB_SRC:-}" ]]; then
  echo "ERROR: \$GTD_KB_SRC is not set." >&2
  echo "Point it to your private knowledge base, e.g.:" >&2
  echo '  export GTD_KB_SRC="$HOME/Documents/GTD知识库"' >&2
  exit 2
fi

if [[ ! -d "${GTD_KB_SRC}" ]]; then
  echo "ERROR: \$GTD_KB_SRC does not exist: ${GTD_KB_SRC}" >&2
  exit 2
fi

APPLY=0
if [[ "${1:-}" == "--apply" ]]; then
  APPLY=1
fi

RSYNC_FLAGS=(
  -a
  --delete
  --exclude='raw/'
  --exclude='.obsidian/'
  --exclude='.DS_Store'
  --exclude='*.tmp'
  --exclude='*.swp'
)

if (( APPLY == 0 )); then
  RSYNC_FLAGS+=(--dry-run --itemize-changes)
  echo "DRY RUN — pass --apply to actually write"
  echo "src:  ${GTD_KB_SRC}/"
  echo "dest: ${DEST}/"
  echo
fi

mkdir -p "${DEST}"
rsync "${RSYNC_FLAGS[@]}" "${GTD_KB_SRC}/" "${DEST}/"

if (( APPLY == 1 )); then
  echo
  echo "✅ mirror updated. Now review and commit:"
  echo "   cd \"${REPO_ROOT}\""
  echo "   git diff knowledge/gtd/"
  echo "   git add knowledge/gtd/ && git commit -m \"sync(kb): refresh from local source\""
fi
