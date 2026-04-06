#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE_DIR="$REPO_ROOT/agents/alfred/profile"
RUNTIME_DIR="$REPO_ROOT/shared/runtime/profile"

mkdir -p "$RUNTIME_DIR"
rm -rf "$RUNTIME_DIR"/*
cp -a "$SOURCE_DIR/." "$RUNTIME_DIR/"
