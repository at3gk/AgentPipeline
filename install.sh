#!/usr/bin/env bash
#
# install.sh - Vendor the agent-pipeline agents and commands into a target repo.
#
# Use this if you would rather copy the files directly into a project than
# install the Claude Code plugin. For the plugin route, see the README.
#
# Usage:
#   ./install.sh [TARGET_DIR]
#
# TARGET_DIR defaults to the current directory. The script copies the agents
# and commands into TARGET_DIR/.claude/ and makes sure .pipeline/ is ignored
# by git.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$SCRIPT_DIR/plugins/agent-pipeline"

TARGET_DIR="${1:-$(pwd)}"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

if [ ! -d "$PLUGIN_DIR/agents" ] || [ ! -d "$PLUGIN_DIR/commands" ]; then
  echo "error: could not find plugin files at $PLUGIN_DIR" >&2
  exit 1
fi

echo "Installing agent-pipeline into: $TARGET_DIR"

mkdir -p "$TARGET_DIR/.claude/agents" "$TARGET_DIR/.claude/commands"

cp "$PLUGIN_DIR"/agents/*.md "$TARGET_DIR/.claude/agents/"
cp "$PLUGIN_DIR"/commands/*.md "$TARGET_DIR/.claude/commands/"

echo "  copied agents   -> .claude/agents/"
echo "  copied commands -> .claude/commands/"

# Keep the handoff folder out of version control.
GITIGNORE="$TARGET_DIR/.gitignore"
if ! { [ -f "$GITIGNORE" ] && grep -qxF ".pipeline/" "$GITIGNORE"; }; then
  printf '\n# Agent pipeline handoff folder\n.pipeline/\n' >> "$GITIGNORE"
  echo "  added .pipeline/ to .gitignore"
fi

echo "Done. Try:  /ship add a hello-world endpoint"
echo "      or:  /ship-overnight <feature>   (autonomous; creates a branch, pushes, no PR)"
