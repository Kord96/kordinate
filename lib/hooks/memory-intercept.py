#!/usr/bin/env python3
"""memory-intercept — PreToolUse hook for Write|Edit.

If target path contains memory/, deny the write and publish the content
to Kafka via the runner's /memory-update HTTP endpoint. All other writes
pass through (allow).
"""

import json
import sys
import os
import urllib.request
from datetime import datetime, timezone

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

    # Only intercept writes to memory/ paths
    if "/memory/" not in file_path:
        allow()

    # Extract the content being written
    content = tool_input.get("content", "") or tool_input.get("new_string", "")
    agent = os.environ.get("AGENT_NAME", "unknown")

    # Publish to runner's /memory-update endpoint
    update = json.dumps({
        "path": file_path,
        "content": content,
        "agent": agent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }).encode()

    try:
        req = urllib.request.Request(
            "http://localhost:9090/memory-update",
            data=update,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        # If runner endpoint is down, still deny the write
        pass

    deny(
        "Memory update queued for curation. "
        "The master curator will merge your insight into the shared memory files."
    )

if __name__ == "__main__":
    main()
