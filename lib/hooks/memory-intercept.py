#!/usr/bin/env python3
"""memory-intercept — PreToolUse guard rail for Write|Edit.

Blocks direct writes to memory/ paths. Agents should use the
/memory-update endpoint instead (see shared/memory-protocol.md).

Claude's internal memory paths (.claude/) are allowed through.
"""

import json
import sys


def allow():
    print("{}")
    sys.exit(0)


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }))
    sys.exit(0)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        allow()

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")

    if not file_path:
        allow()

    # Only guard memory/ paths
    if "/memory/" not in file_path:
        allow()

    # Allow Claude's internal memory
    if "/.claude/" in file_path:
        allow()

    deny(
        "Direct writes to memory/ are not allowed. "
        "Use the memory endpoint instead: "
        "curl -s http://localhost:9090/memory-update "
        '-H "Content-Type: application/json" '
        "-d '{\"path\":\"<topic>.md\",\"content\":\"...\",\"scope\":\"global|project\",\"project\":\"...\"}'"
    )


if __name__ == "__main__":
    main()
