#!/bin/bash
# runtime-sync — after git commit in a kordinate worktree, sync changed files to runtime.
#
# Registered as PostToolUse on Bash. Triggers on git commit from a
# worktree that contains the kordinate/ package directory.
#
# Syncs: agent identities → ~/.claude/agents/
#        agent skills/memory → $WORKSTATION_HOME/kordinate/agents/ (global memory)
#        team skills → ~/.claude/skills/
#        server code → $WORKSTATION_HOME/kordinate/lib/

set -uo pipefail

log() { echo "[runtime-sync] $*" >&2; }

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
[ -n "$CMD" ] || exit 0

# Only act on git commit
echo "$CMD" | grep -qE 'git\s+((-C\s+\S+\s+)?commit)' || exit 0

# Determine repo root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
[ -n "$REPO_ROOT" ] || exit 0

# Must contain the kordinate package
KORD_PKG="$REPO_ROOT/kordinate"
[ -d "$KORD_PKG" ] || exit 0

WORKSTATION_HOME="${WORKSTATION_HOME:-$HOME}"
RUNTIME_ROOT="${RUNTIME_ROOT:-$WORKSTATION_HOME/kordinate}"
CLAUDE_DIR="$HOME/.claude"

# --- Sync agent identities → ~/.claude/agents/ ---
for identity in "$KORD_PKG"/agents/*/IDENTITY.md; do
  [ -f "$identity" ] || continue
  agent=$(basename "$(dirname "$identity")")
  cp "$identity" "$CLAUDE_DIR/agents/$agent.md" 2>/dev/null
done

# --- Sync agent skills and global memory → workstation runtime ---
for agent_dir in "$KORD_PKG"/agents/*/; do
  agent=$(basename "$agent_dir")
  # Skills
  if [ -d "$agent_dir/skills" ]; then
    mkdir -p "$RUNTIME_ROOT/agents/$agent/skills"
    cp -r "$agent_dir/skills/"* "$RUNTIME_ROOT/agents/$agent/skills/" 2>/dev/null
  fi
  # Global memory (top-level .md files only, not concept subdirs)
  if [ -d "$agent_dir/memory/global" ]; then
    mkdir -p "$RUNTIME_ROOT/agents/$agent/memory/global"
    for f in "$agent_dir"/memory/global/*.md; do
      [ -f "$f" ] && cp "$f" "$RUNTIME_ROOT/agents/$agent/memory/global/" 2>/dev/null
    done
  fi
done

# --- Sync shared skills → ~/.claude/skills/ ---
for skill_dir in "$KORD_PKG"/shared/skills/*/; do
  skill=$(basename "$skill_dir")
  mkdir -p "$CLAUDE_DIR/skills/$skill"
  cp "$skill_dir"/*.md "$CLAUDE_DIR/skills/$skill/" 2>/dev/null
done

# --- Sync kord MCP server → workstation runtime ---
if [ -f "$KORD_PKG/shared/kord-mcp/dist/server.js" ]; then
  mkdir -p "$RUNTIME_ROOT/shared/kord-mcp/dist" "$RUNTIME_ROOT/shared/kord-mcp/bin"
  cp "$KORD_PKG/shared/kord-mcp/dist/server.js" "$RUNTIME_ROOT/shared/kord-mcp/dist/server.js" 2>/dev/null
  cp "$KORD_PKG/shared/kord-mcp/bin/kord-mcp" "$RUNTIME_ROOT/shared/kord-mcp/bin/kord-mcp" 2>/dev/null
fi


log "synced kordinate → runtime"
exit 0
