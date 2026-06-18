#!/usr/bin/env bash
#
# install.sh - Vendor the marketplace plugins into a target repo.
#
# Copies the agent-pipeline and storm-research agents, commands, and skills
# directly into a project, so you can use them without the Claude Code plugin
# system. For the plugin route (recommended), see the README.
#
# Usage:
#   ./install.sh [TARGET_DIR]
#
# TARGET_DIR defaults to the current directory. The script copies the files
# into TARGET_DIR/.claude/ and makes sure .pipeline/ is ignored by git.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGINS_DIR="$SCRIPT_DIR/plugins"

TARGET_DIR="${1:-$(pwd)}"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

if [ ! -d "$PLUGINS_DIR/agent-pipeline" ]; then
  echo "error: could not find plugins at $PLUGINS_DIR" >&2
  exit 1
fi

echo "Installing plugins into: $TARGET_DIR"

mkdir -p "$TARGET_DIR/.claude/agents" "$TARGET_DIR/.claude/commands" "$TARGET_DIR/.claude/skills"

# Copy every plugin's agents, commands, and skills (each is optional per plugin).
for PLUGIN_DIR in "$PLUGINS_DIR"/*/; do
  name="$(basename "$PLUGIN_DIR")"
  [ -d "$PLUGIN_DIR/agents" ]   && cp "$PLUGIN_DIR"agents/*.md   "$TARGET_DIR/.claude/agents/"   2>/dev/null || true
  [ -d "$PLUGIN_DIR/commands" ] && cp "$PLUGIN_DIR"commands/*.md "$TARGET_DIR/.claude/commands/" 2>/dev/null || true
  if [ -d "$PLUGIN_DIR/skills" ]; then
    cp -R "$PLUGIN_DIR"skills/. "$TARGET_DIR/.claude/skills/"
  fi
  echo "  vendored $name"
done

echo "  agents   -> .claude/agents/"
echo "  commands -> .claude/commands/"
echo "  skills   -> .claude/skills/"

# Keep the pipeline handoff folder out of version control.
GITIGNORE="$TARGET_DIR/.gitignore"
if ! { [ -f "$GITIGNORE" ] && grep -qxF ".pipeline/" "$GITIGNORE"; }; then
  printf '\n# Agent pipeline handoff folder\n.pipeline/\n' >> "$GITIGNORE"
  echo "  added .pipeline/ to .gitignore"
fi

echo "Done. Try:  /map-repo                 (index canonical patterns -> REPO_CONTRACT.md)"
echo "      then: /ship add a hello-world endpoint"
echo "      or:  /storm <topic>            (STORM research briefing -> research/<slug>.md)"
echo "      or:  /ship-overnight <feature> (autonomous; creates a branch, pushes, no PR)"
