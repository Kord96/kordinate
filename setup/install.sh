#!/bin/bash
# Install koordinate framework files to ~/.claude/.
# Copies agents, commands, CLAUDE.md, MCP config, and profile.
# Preserves existing mutable files (inbox.md, profile data).
#
# Called by: ./setup.sh install
# Idempotent: safe to run multiple times.

set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"

echo "Installing koordinate framework → $CLAUDE_DIR"

# Create directory structure
mkdir -p "$CLAUDE_DIR"/{commands,agents,agent-state,profile}

# ─── Copy standalone commands ───
if [ -d "$CLAUDE_HOME/commands" ] && [ "$(ls -A "$CLAUDE_HOME/commands" 2>/dev/null)" ]; then
  for f in "$CLAUDE_HOME/commands"/*; do
    base="$(basename "$f")"
    cp -r "$f" "$CLAUDE_DIR/commands/$base"
    echo "  COPY commands/$base"
  done
fi

# ─── Copy scribe agent commands (utility-safe, handles own auth) ───
if [ -d "$CLAUDE_HOME/agents/scribe/commands" ]; then
  mkdir -p "$CLAUDE_DIR/commands/scribe"
  cp -r "$CLAUDE_HOME/agents/scribe/commands/"* "$CLAUDE_DIR/commands/scribe/"
  echo "  COPY commands/scribe/ (all scribe commands)"
fi

# ─── Copy agents (definitions only: CLAUDE.md, commands/, knowledge/) ───
for agent_dir in "$CLAUDE_HOME/agents"/*/; do
  [ -d "$agent_dir" ] || continue
  agent="$(basename "$agent_dir")"
  dest="$CLAUDE_DIR/agents/$agent"
  mkdir -p "$dest"

  # Copy CLAUDE.md
  if [ -f "$agent_dir/CLAUDE.md" ]; then
    cp "$agent_dir/CLAUDE.md" "$dest/CLAUDE.md"
    echo "  COPY agents/$agent/CLAUDE.md"
  fi

  # Copy commands/
  if [ -d "$agent_dir/commands" ] && [ "$(ls -A "$agent_dir/commands" 2>/dev/null)" ]; then
    mkdir -p "$dest/commands"
    cp -r "$agent_dir/commands/"* "$dest/commands/"
    echo "  COPY agents/$agent/commands/"
  fi

  # Copy knowledge/ (framework docs — not index.yaml which is sensitive)
  if [ -d "$agent_dir/knowledge" ]; then
    mkdir -p "$dest/knowledge"
    for f in "$agent_dir/knowledge"/*.md; do
      [ -f "$f" ] && cp "$f" "$dest/knowledge/"
    done
    echo "  COPY agents/$agent/knowledge/*.md"
  fi

  # Create inbox.md if missing (preserve existing)
  if [ ! -f "$dest/inbox.md" ]; then
    echo "# Inbox" > "$dest/inbox.md"
    echo "  CREATE agents/$agent/inbox.md"
  else
    echo "  SKIP agents/$agent/inbox.md (already exists)"
  fi
done

# ─── Copy CLAUDE.md ───
if [ -f "$CLAUDE_HOME/CLAUDE.md" ]; then
  cp "$CLAUDE_HOME/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
  echo "  COPY CLAUDE.md"
fi

# ─── Copy profile/ if it exists in the repo (preserves existing in ~/.claude/) ───
if [ -d "$CLAUDE_HOME/profile" ] && [ "$(ls -A "$CLAUDE_HOME/profile" 2>/dev/null)" ]; then
  # Copy profile files, preserving existing ones at destination
  for item in "$CLAUDE_HOME/profile"/*; do
    base="$(basename "$item")"
    dest="$CLAUDE_DIR/profile/$base"
    if [ -d "$item" ]; then
      mkdir -p "$dest"
      cp -rn "$item/"* "$dest/" 2>/dev/null || cp -r "$item/"* "$dest/" 2>/dev/null || true
    elif [ -f "$item" ] && [ ! -f "$dest" ]; then
      cp "$item" "$dest"
    fi
  done
  echo "  COPY profile/ (new files only — existing preserved)"
fi

# ─── Copy config files to ~/.claude/ (if they exist in repo, preserve existing) ───
for f in config.yaml .mcp.json mcp-global.json; do
  if [ -f "$CLAUDE_HOME/$f" ] && [ ! -f "$CLAUDE_DIR/$f" ]; then
    cp "$CLAUDE_HOME/$f" "$CLAUDE_DIR/$f"
    echo "  COPY $f"
  fi
done

# ─── Install MCP config ───
# mcp-global.json or .mcp.json → ~/.claude/.mcp.json
if [ -f "$CLAUDE_DIR/mcp-global.json" ]; then
  cp "$CLAUDE_DIR/mcp-global.json" "$CLAUDE_DIR/.mcp.json"
  echo "  COPY .mcp.json (from mcp-global.json)"
elif [ ! -f "$CLAUDE_DIR/.mcp.json" ]; then
  echo "  SKIP .mcp.json (no source file — run ./setup.sh profile to scaffold)"
fi

# ─── Copy hooks to ~/.claude/hooks/ ───
if [ -d "$CLAUDE_HOME/hooks" ]; then
  mkdir -p "$CLAUDE_DIR/hooks"
  for f in "$CLAUDE_HOME/hooks"/*.sh; do
    [ -f "$f" ] || continue
    cp "$f" "$CLAUDE_DIR/hooks/"
    chmod +x "$CLAUDE_DIR/hooks/$(basename "$f")"
    echo "  COPY hooks/$(basename "$f")"
  done
fi

# ─── Configure global settings.json with hooks ───
# Only add hooks if not already configured
SETTINGS="$CLAUDE_DIR/settings.json"
if [ ! -f "$SETTINGS" ] || ! grep -q 'guard-md.sh' "$SETTINGS" 2>/dev/null; then
  cat > "$SETTINGS" << 'SETTINGS_JSON'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/guard-md.sh"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/guard-kubectl.sh"
          },
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/guard-git.sh"
          }
        ]
      },
      {
        "matcher": "mcp__grafana",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/guard-grafana.sh"
          }
        ]
      },
      {
        "matcher": "mcp__redis",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/guard-redis.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/auto-merge-to-dev.sh"
          }
        ]
      }
    ]
  }
}
SETTINGS_JSON
  echo "  CREATE settings.json (global hooks)"
else
  echo "  SKIP settings.json (hooks already configured)"
fi

# ─── Generate guard hook auth secrets ───
for agent_secret in scribe deployer sauron; do
  secret_file="$CLAUDE_DIR/.${agent_secret}-secret"
  if [ ! -f "$secret_file" ]; then
    openssl rand -hex 16 > "$secret_file"
    echo "  CREATE .${agent_secret}-secret"
  else
    echo "  SKIP .${agent_secret}-secret (already exists)"
  fi
done

# ─── Cleanup: remove files from ~/.claude/ that no longer exist in kordinate ───
echo "Cleaning up stale files..."

# Cleanup standalone commands
if [ -d "$CLAUDE_DIR/commands" ]; then
  for f in "$CLAUDE_DIR/commands"/*; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"
    # Skip scribe/ directory (handled separately)
    [ "$base" = "scribe" ] && continue
    if [ ! -e "$CLAUDE_HOME/commands/$base" ]; then
      rm -rf "$f"
      echo "  REMOVE commands/$base (deleted from source)"
    fi
  done
fi

# Cleanup scribe commands
if [ -d "$CLAUDE_DIR/commands/scribe" ]; then
  for f in "$CLAUDE_DIR/commands/scribe"/*; do
    [ -f "$f" ] || continue
    base="$(basename "$f")"
    if [ ! -f "$CLAUDE_HOME/agents/scribe/commands/$base" ]; then
      rm "$f"
      echo "  REMOVE commands/scribe/$base (deleted from source)"
    fi
  done
fi

# Cleanup agent commands and knowledge
for agent_dir in "$CLAUDE_DIR/agents"/*/; do
  [ -d "$agent_dir" ] || continue
  agent="$(basename "$agent_dir")"
  src="$CLAUDE_HOME/agents/$agent"

  # Remove entire agent if deleted from source
  if [ ! -d "$src" ]; then
    rm -rf "$agent_dir"
    echo "  REMOVE agents/$agent/ (deleted from source)"
    continue
  fi

  # Cleanup commands/
  if [ -d "$agent_dir/commands" ]; then
    for f in "$agent_dir/commands"/*; do
      [ -f "$f" ] || continue
      base="$(basename "$f")"
      if [ ! -f "$src/commands/$base" ]; then
        rm "$f"
        echo "  REMOVE agents/$agent/commands/$base (deleted from source)"
      fi
    done
  fi

  # Cleanup knowledge/*.md
  if [ -d "$agent_dir/knowledge" ]; then
    for f in "$agent_dir/knowledge"/*.md; do
      [ -f "$f" ] || continue
      base="$(basename "$f")"
      if [ ! -f "$src/knowledge/$base" ]; then
        rm "$f"
        echo "  REMOVE agents/$agent/knowledge/$base (deleted from source)"
      fi
    done
  fi
done

# Cleanup hooks
if [ -d "$CLAUDE_DIR/hooks" ] && [ -d "$CLAUDE_HOME/hooks" ]; then
  for f in "$CLAUDE_DIR/hooks"/*.sh; do
    [ -f "$f" ] || continue
    base="$(basename "$f")"
    if [ ! -f "$CLAUDE_HOME/hooks/$base" ]; then
      rm "$f"
      echo "  REMOVE hooks/$base (deleted from source)"
    fi
  done
fi

echo ""
echo "Install complete. Runtime at: $CLAUDE_DIR"
