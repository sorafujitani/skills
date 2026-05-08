#!/usr/bin/env bash
# Package a Claude Code skill into a ZIP for Claude Desktop upload.
#
# Usage: zip_skill.sh <name> [<source-dir>] [<output-path>]
#   name        — skill name (becomes ZIP root dir and filename)
#   source-dir  — defaults to ~/.claude/skills/<name>
#   output-path — defaults to ~/Downloads/<name>.zip

set -euo pipefail

NAME="${1:?skill name required (arg 1)}"
SOURCE="${2:-$HOME/.claude/skills/$NAME}"
OUT="${3:-$HOME/Downloads/$NAME.zip}"

[[ -d "$SOURCE" ]] || { echo "ERROR: source dir not found: $SOURCE" >&2; exit 1; }
[[ -f "$SOURCE/SKILL.md" ]] || { echo "ERROR: $SOURCE has no SKILL.md" >&2; exit 1; }

# Stage in a temp dir so the ZIP root is exactly <name>/
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cp -R "$SOURCE" "$TMP/$NAME"

# Strip macOS / Python junk
find "$TMP/$NAME" \
  \( -name ".DS_Store" -o -name "__pycache__" -o -name "*.pyc" \) \
  -exec rm -rf {} + 2>/dev/null || true

# Overwrite any previous output
rm -f "$OUT"

(cd "$TMP" && zip -r -q "$OUT" "$NAME")

echo "$OUT"
