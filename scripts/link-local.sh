#!/usr/bin/env bash
# Symlink each skill in this repo into the user's Claude skills directory.
# Lets the author edit skills here and have changes reflected in Claude Code
# immediately, without going through `npx skills add ...` (which copies).
#
# Each top-level directory containing a SKILL.md file is treated as a skill.
#
# Usage:
#   scripts/link-local.sh           # create or update symlinks
#   scripts/link-local.sh --dry-run # show what would happen, change nothing
#   scripts/link-local.sh --unlink  # remove only the symlinks we created
#   scripts/link-local.sh --help    # show this help
#
# Env:
#   CLAUDE_USER_SKILLS_DIR  override target dir (default: ~/.claude/skills)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${CLAUDE_USER_SKILLS_DIR:-$HOME/.claude/skills}"

DRY_RUN=0
UNLINK=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --unlink)  UNLINK=1 ;;
    -h|--help)
      sed -n '2,/^set -euo pipefail$/p' "$0" | sed 's/^# \?//;$d'
      exit 0
      ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

run() {
  if (( DRY_RUN )); then
    echo "DRY: $*"
  else
    "$@"
  fi
}

mkdir -p "$TARGET_DIR"

shopt -s nullglob
status=0

for skill_dir in "$ROOT"/*/; do
  src="${skill_dir%/}"
  [[ -f "$src/SKILL.md" ]] || continue

  skill_name="$(basename "$src")"
  link="$TARGET_DIR/$skill_name"

  if (( UNLINK )); then
    if [[ -L "$link" && "$(readlink "$link")" == "$src" ]]; then
      run rm "$link"
      echo "unlinked: $skill_name"
    fi
    continue
  fi

  if [[ -L "$link" ]]; then
    current="$(readlink "$link")"
    if [[ "$current" == "$src" ]]; then
      echo "ok      : $skill_name"
      continue
    fi
    echo "updating: $skill_name (was -> $current)"
    run ln -sfn "$src" "$link"
    continue
  fi

  if [[ -e "$link" ]]; then
    echo "SKIP    : $skill_name (real entry exists at $link, refusing to overwrite)" >&2
    status=1
    continue
  fi

  run ln -s "$src" "$link"
  echo "linked  : $skill_name -> $src"
done

exit $status
