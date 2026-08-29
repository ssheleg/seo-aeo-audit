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

# One channel per agent: a plain copy beside an installed plugin is two listings
# of the same skill, and the stale one wins. Refuse rather than create that, and
# refuse loudly — a refusal that exits 0 reads as success to every script above
# it. installed_plugins.json is the record of what is installed; the
# marketplaces/ dir is kept only as a fallback signal, because a
# directory-sourced marketplace has no dir there and plugin names differ from
# marketplace names. A missing or unparsable JSON reads as "no plugin".
INSTALLED_JSON="${HOME}/.claude/plugins/installed_plugins.json"
MARKETPLACE="${HOME}/.claude/plugins/marketplaces/seo-aeo-audit"
SPEC=""
if [[ -f "$INSTALLED_JSON" ]]; then
  SPEC="$(sed -n 's/.*"\(seo-aeo-audit@[^"]*\)".*/\1/p' "$INSTALLED_JSON" 2>/dev/null | head -n 1)" || true
fi
if [[ ( -n "$SPEC" || -e "$MARKETPLACE" ) && "$FORCE" -eq 0 ]]; then
  {
    if [[ -n "$SPEC" ]]; then
      echo "refused: seo-aeo-audit is already installed as the Claude Code plugin $SPEC"
      echo "         (declared in ~/.claude/plugins/installed_plugins.json)."
    else
      echo "refused: seo-aeo-audit is already registered as a Claude Code marketplace"
      echo "         ($MARKETPLACE)."
    fi
    echo "         A plain copy in ~/.claude/skills would shadow the plugin and serve"
    echo "         this frozen version forever. Update the plugin channel instead:"
    echo "           claude plugin marketplace update seo-aeo-audit"
    echo "           claude plugin update ${SPEC:-seo-aeo-audit@seo-aeo-audit}"
    echo "         Family launcher: npx --yes sshlg-skills@latest update"
    echo "         Pass --force to write the plain copy anyway."
  } >&2
  exit 3
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

# The last lines say how the next version arrives and when it takes effect.
echo "Updates: git pull && ./install.sh --force, or npx --yes sshlg-skills@latest update"
echo "Restart Claude Code (or start a new session) to load it — skills are read at session start."
