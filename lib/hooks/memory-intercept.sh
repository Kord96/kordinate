#!/bin/bash
# memory-intercept.sh — PreToolUse hook for Write|Edit
# Delegates to python3 for reliable JSON parsing.
exec python3 /data/repos/kordinate/lib/hooks/memory-intercept.py
