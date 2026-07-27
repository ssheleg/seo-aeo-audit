#!/usr/bin/env bash
# Installs the seo-aeo-audit skill + /seo-aeo-audit command into ~/.claude.
# Idempotent: skips anything already installed; pass --force to overwrite.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
elif [[ -n "${1:-}" ]]; then
  echo "usage: $0 [--force]" >&2
  exit 2
fi

# 1. skill
SRC="$HERE/plugins/seo-aeo-audit/skills/seo-aeo-audit"
DEST="${HOME}/.claude/skills/seo-aeo-audit"
if [[ -e "$DEST" && "$FORCE" -eq 0 ]]; then
  echo "skip: skill already installed at $DEST (rerun with --force to overwrite)"
else
  mkdir -p "$(dirname "$DEST")"
  rm -rf "$DEST"
  cp -R "$SRC" "$DEST"
  echo "Installed seo-aeo-audit skill   -> $DEST"
fi

# 2. slash command
CMD_SRC="$HERE/plugins/seo-aeo-audit/commands/seo-aeo-audit.md"
CMD_DEST="${HOME}/.claude/commands/seo-aeo-audit.md"
if [[ -e "$CMD_DEST" && "$FORCE" -eq 0 ]]; then
  echo "skip: command already installed at $CMD_DEST (rerun with --force to overwrite)"
else
  mkdir -p "$(dirname "$CMD_DEST")"
  cp "$CMD_SRC" "$CMD_DEST"
  echo "Installed /seo-aeo-audit command -> $CMD_DEST"
fi
